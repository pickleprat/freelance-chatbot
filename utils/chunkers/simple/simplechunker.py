from ..chunker import Chunker 
from ..models.simplechunk import SimpleChunk
from ..settings.simplesettings import SimpleSettings

class CharacterSplitChunker(Chunker): 
    @classmethod
    def split_text(cls, content: str, settings: SimpleSettings) -> list[SimpleChunk]: 
        chunks: list[SimpleChunk] = []

        chunk_size = settings.chunk_size
        overlap = settings.overlap

        start = 0
        chunk_index = 1

        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_content = content[start:end]

            chunk_id = f"chunk_{chunk_index:03d}"

            chunks.append(SimpleChunk(
                _id=chunk_id,
                chunk_text=chunk_content,
            ))

            start += chunk_size - overlap
            chunk_index += 1

        return chunks

    

