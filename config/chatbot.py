import dotenv 
import os 

dotenv.load_dotenv(override=True)

class Config: 
    NEON_CONNECTION_STRING  : str = os.getenv("NEON_CONNECTION_STRING")
    PINECONE_SERVERLESS_KEY : str = os.getenv("PINECONE_API_KEY")
    GEMINI_API_KEY          : str = os.getenv("GEMINI_API_KEY")
    NAMESPACE               : str = os.getenv("NAMESPACE")


