from pinecone import Pinecone
from ...config.chatbot import Config

class PineconeProvider: 
    @classmethod
    def get_connection(cls) -> Pinecone | None: 
        try: 
            return Pinecone(Config.PINECONE_SERVERLESS_KEY)
        except Exception as err: 
            return None
    

