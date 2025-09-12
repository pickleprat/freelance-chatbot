from pinecone import Pinecone, ServerlessSpec
from ...config.chatbot import Config

class PineconeProvider: 
    __conn = None 

