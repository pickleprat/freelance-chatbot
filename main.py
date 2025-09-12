from databases.neondb.service.pdfcontent.pdfcontentservice import PDFContentService
from databases.neondb.service.pdfcontent.model import PdfContent
from utils.preprocessor.chunker import DocumentChunker, Chunk


pdf_content = PDFContentService()
content: PdfContent  = pdf_content.get_all_content(limit=1)[0]
chunker = DocumentChunker(
    chunk_size=400, 
    overlap_size=100,
    min_chunk_size=100
)

chunks: list[Chunk] = chunker.chunk_document(
    content=content.content, 
    chunk_id_marker=content.id, 
    document_type="directory", 
)


    # Display results
print(f"Created {len(chunks)} chunks:")
print("=" * 50)

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i + 1}:")
    print(f"Content: {chunk.content[:200]}...")
    print(f"Department: {chunk.department}")
    print(f"People: {chunk.people}")
    print(f"Roles: {chunk.roles}")
    print(f"Contacts: {chunk.contacts}")
    print(f"Overlap refs: {chunk.overlap_references}")
    print("-" * 30)