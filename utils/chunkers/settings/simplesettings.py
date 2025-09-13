from utils.chunkers.settings.settings import Settings

class SimpleSettings(Settings): 
    chunk_size: int = 800
    overlap   : int = 50