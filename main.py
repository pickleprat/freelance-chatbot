from databases.neondb.service.pdfcontent.pdfcontentservice import PDFContentService
from databases.neondb.service.pdfcontent.model import PdfContent
from databases.pinecone.service.query.pinecone import PineconeService
from databases.pinecone.models.options import PineconeOptions

from utils.chunkers.simple.simplechunker import CharacterSplitChunker
from utils.chunkers.models.simplechunk import SimpleChunk
from utils.chunkers.settings.simplesettings import SimpleSettings
from config.chatbot import Config 


pdf_content = PDFContentService()
content: PdfContent  = pdf_content.get_all_content(limit=1)[0]
settings: SimpleSettings = SimpleSettings(chunk_size=1000, overlap=400)
chunks: list[SimpleChunk] = CharacterSplitChunker.split_text(content.content, settings=settings)

options: PineconeOptions = PineconeOptions(name=Config.INDEX_NAME)
pcService: PineconeService = PineconeService(options=options)
upsertStatus: bool = pcService.upsert(chunks)

if upsertStatus: 
    print("upserted success!")
else: 
    print("FAILURE!")
