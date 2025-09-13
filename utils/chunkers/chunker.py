from abc import ABC, abstractmethod
from utils.chunkers.models.chunk import Chunk 
from utils.chunkers.settings.settings import Settings

class Chunker(ABC): 
    @classmethod
    @abstractmethod
    def split_text(cls, content: str, settings: Settings) -> list[Chunk]: 
        pass 