from databases.pinecone.service.query.pinecone import PineconeService
from databases.pinecone.models.options import PineconeOptions

from config.chatbot import Config 


options: PineconeOptions = PineconeOptions(name=Config.INDEX_NAME)
pcService: PineconeService = PineconeService(options=options)

