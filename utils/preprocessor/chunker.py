import re
from dataclasses import dataclass, asdict
from datetime import datetime
import spacy

try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None

@dataclass
class Chunk: 
    chunk_text: str
    chunk_id: str
    chunk_id_marker: str
    
@dataclass
class EnrichedChunk(Chunk):
    """Represents a chunk of company information with rich metadata"""
    document_type: str
    department: str = None
    location: str = None
    people: list[str] = None
    roles: list[str] = None
    contacts: dict[str, str] = None
    created_date: str = None
    chunk_size: int = 0
    overlap_references: list[str] = None
    
    def __post_init__(self):
        if self.people is None:
            self.people = []
        if self.contacts is None:
            self.contacts = {}
        if self.overlap_references is None:
            self.overlap_references = []
        if self.created_date is None:
            self.created_date = datetime.now().isoformat()
        self.chunk_size = len(self.content)

class DocumentChunker:
    """Advanced chunking system for company documents"""
    
    def __init__(self, 
                 chunk_size: int = 500, 
                 overlap_size: int = 100,
                 min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size
        
        # Patterns for extracting company information
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}\b'),
            'department': re.compile(r'\b(?:Department|Dept|Division|Team|Unit|Group)[\s:]?\s*([A-Za-z\s&]+)', re.IGNORECASE),
            'role_titles': re.compile(r'\b(?:Director|Manager|Lead|Senior|Junior|Assistant|VP|President|CEO|CTO|CFO|Head of|Chief)\b[A-Za-z\s]*', re.IGNORECASE),
            'location': re.compile(r'\b(?:Office|Building|Floor|Room|Suite|Address)[\s:]?\s*([A-Za-z0-9\s,.-]+)', re.IGNORECASE)
        }
        
        # Common department keywords
        self.department_keywords = {
            'hr', 'human resources', 'finance', 'accounting', 'marketing', 'sales',
            'engineering', 'development', 'it', 'operations', 'legal', 'compliance',
            'research', 'r&d', 'customer service', 'support', 'administration'
        }
    
    def extract_entities(self, text: str) -> dict[str, any]:
        """Extract various entities from text using regex and NLP"""
        entities = {
            'people': [],
            'emails': [],
            'phones': [],
            'departments': [],
            'roles': [],
            'locations': [],
            'organizations': []
        }
        
        # Extract using regex patterns
        entities['emails'] = self.patterns['email'].findall(text)
        entities['phones'] = self.patterns['phone'].findall(text)
        
        # Extract departments
        dept_matches = self.patterns['department'].findall(text)
        entities['departments'].extend([match.strip() for match in dept_matches])
        
        # Extract role titles
        role_matches = self.patterns['role_titles'].findall(text)
        entities['roles'].extend([match.strip() for match in role_matches])
        
        # Extract locations
        location_matches = self.patterns['location'].findall(text)
        entities['locations'].extend([match.strip() for match in location_matches])
        
        # Use spaCy for named entity recognition if available
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities['people'].append(ent.text.strip())
                elif ent.label_ == "ORG":
                    entities['organizations'].append(ent.text.strip())
                elif ent.label_ in ["GPE", "LOC"]:
                    entities['locations'].append(ent.text.strip())
        
        # Clean and deduplicate
        for key in entities:
            entities[key] = list(set([item for item in entities[key] if item]))
        
        return entities
    
    def identify_document_type(self, content: str, filename: str = "") -> str:
        """Identify document type based on content and filename"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        type_indicators = {
            'org_chart': ['organizational chart', 'org chart', 'hierarchy', 'reporting structure'],
            'directory': ['directory', 'contact list', 'phone book', 'employee list'],
            'handbook': ['employee handbook', 'manual', 'policies', 'procedures'],
            'job_description': ['job description', 'role description', 'responsibilities'],
            'announcement': ['announcement', 'press release', 'memo', 'update'],
            'profile': ['profile', 'biography', 'bio', 'about']
        }
        
        # Check filename first
        for doc_type, keywords in type_indicators.items():
            if any(keyword in filename_lower for keyword in keywords):
                return doc_type
        
        # Check content
        for doc_type, keywords in type_indicators.items():
            if any(keyword in content_lower for keyword in keywords):
                return doc_type
        
        return 'general'
    
    def find_contextual_boundaries(self, text: str, entities: dict[str, any]) -> list[int]:
        """Find natural boundaries that keep related information together"""
        boundaries = [0]
        sentences = re.split(r'[.!?]+', text)
        current_pos = 0
        
        for i, sentence in enumerate(sentences):
            sentence_start = text.find(sentence, current_pos)
            if sentence_start == -1:
                continue
            
            sentence_end = sentence_start + len(sentence)
            current_pos = sentence_end
            
            # Check if this sentence contains important entities
            sentence_entities = self.extract_entities(sentence)
            has_person = bool(sentence_entities['people'])
            has_role = bool(sentence_entities['roles'])
            has_contact = bool(sentence_entities['emails'] or sentence_entities['phones'])
            
            # Create boundary if we have a complete "unit" of information
            if has_person and (has_role or has_contact):
                if sentence_end - boundaries[-1] > self.min_chunk_size:
                    boundaries.append(sentence_end)
        
        # Add final boundary
        if boundaries[-1] < len(text):
            boundaries.append(len(text))
        
        return boundaries
    
    def create_overlapping_chunks(self, text: str, boundaries: list[int]) -> list[tuple[str, list[str]]]:
        """Create chunks with overlapping content and track references"""
        chunks = []
        
        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]
            
            # Extend chunk size if too small
            if end - start < self.min_chunk_size and i < len(boundaries) - 2:
                end = min(boundaries[i + 2], start + self.chunk_size)
            
            chunk_content = text[start:end].strip()
            
            # Create overlaps with previous and next chunks
            overlap_refs = []
            
            # Overlap with previous chunk
            if i > 0:
                overlap_start = max(0, start - self.overlap_size)
                overlap_content = text[overlap_start:start].strip()
                if overlap_content:
                    chunk_content = overlap_content + " " + chunk_content
                    overlap_refs.append(f"chunk_{i-1}")
            
            # Overlap with next chunk
            if i < len(boundaries) - 2:
                overlap_end = min(len(text), end + self.overlap_size)
                overlap_content = text[end:overlap_end].strip()
                if overlap_content:
                    chunk_content = chunk_content + " " + overlap_content
                    overlap_refs.append(f"chunk_{i+1}")
            
            chunks.append((chunk_content, overlap_refs))
        
        return chunks
    
    def extract_contacts_from_chunk(self, text: str, entities: dict[str, any]) -> dict[str, str]:
        """Extract and associate contact information"""
        contacts = {}
        
        # Simple association: if email/phone appears near a person name
        for person in entities['people']:
            person_context = self.get_context_around_person(text, person, window=200)
            
            # Find emails in context
            context_emails = self.patterns['email'].findall(person_context)
            if context_emails:
                contacts[f"{person}_email"] = context_emails[0]
            
            # Find phones in context
            context_phones = self.patterns['phone'].findall(person_context)
            if context_phones:
                contacts[f"{person}_phone"] = context_phones[0]
        
        # General contact info
        if entities['emails']:
            contacts['general_email'] = entities['emails'][0]
        if entities['phones']:
            contacts['general_phone'] = entities['phones'][0]
        
        return contacts
    
    def get_context_around_person(self, text: str, person: str, window: int = 200) -> str:
        """Get text context around a person's name"""
        person_pos = text.lower().find(person.lower())
        if person_pos == -1:
            return ""
        
        start = max(0, person_pos - window)
        end = min(len(text), person_pos + len(person) + window)
        return text[start:end]
    
    def infer_department(self, text: str, entities: dict[str, any]) -> str:
        """Infer department from context and entities"""
        text_lower = text.lower()
        
        # Check explicit department mentions
        if entities['departments']:
            return entities['departments'][0]
        
        # Check for department keywords
        for dept in self.department_keywords:
            if dept in text_lower:
                return dept.title()
        
        # Infer from role titles
        for role in entities['roles']:
            role_lower = role.lower()
            if any(tech_word in role_lower for tech_word in ['engineer', 'developer', 'tech', 'it']):
                return "Engineering"
            elif any(sales_word in role_lower for sales_word in ['sales', 'account', 'business development']):
                return "Sales"
            elif any(hr_word in role_lower for hr_word in ['hr', 'human resources', 'recruiter']):
                return "Human Resources"
        
        return None
    
    def chunk_document(self, 
                      content: str, 
                      chunk_id_marker: str,
                      document_type: str = None,
                      metadata: dict[str, any] = None) -> list[EnrichedChunk]:
        """Main chunking method that creates contextual chunks with rich metadata"""
        
        if not content.strip():
            return []
        
        # Identify document type if not provided
        if document_type is None:
            document_type = self.identify_document_type(content, chunk_id_marker)
        
        # Extract entities from full document for context
        full_doc_entities = self.extract_entities(content)
        
        # Find contextual boundaries
        boundaries = self.find_contextual_boundaries(content, full_doc_entities)
        
        # Create overlapping chunks
        chunk_tuples = self.create_overlapping_chunks(content, boundaries)
        
        # Convert to Chunk objects
        chunks = []
        for i, (chunk_content, overlap_refs) in enumerate(chunk_tuples):
            # Extract entities for this specific chunk
            chunk_entities = self.extract_entities(chunk_content)
            
            # Create contacts dictionary
            contacts = self.extract_contacts_from_chunk(chunk_content, chunk_entities)
            
            # Infer metadata
            inferred_dept = self.infer_department(chunk_content, chunk_entities)
            
            chunk = EnrichedChunk(
                content=chunk_content,
                chunk_id=f"{chunk_id_marker}_{i}",
                chunk_id_marker=chunk_id_marker,
                document_type=document_type,
                department=inferred_dept,
                location=chunk_entities['locations'][0] if chunk_entities['locations'] else None,
                people=chunk_entities['people'],
                roles=chunk_entities['roles'],
                contacts=contacts,
                overlap_references=overlap_refs
            )
            
            # Add any additional metadata passed in
            if metadata:
                for key, value in metadata.items():
                    if hasattr(chunk, key):
                        setattr(chunk, key, value)
            
            chunks.append(chunk)
        
        return chunks
    
    def chunk_to_dict(self, chunk: EnrichedChunk) -> dict[str, any]:
        """Convert chunk to dictionary for storage"""
        return asdict(chunk)
    
    def chunk_from_dict(self, chunk_dict: dict[str, any]) -> EnrichedChunk:
        """Convert dictionary back to Enriched Chunk"""
        return EnrichedChunk(**chunk_dict)
