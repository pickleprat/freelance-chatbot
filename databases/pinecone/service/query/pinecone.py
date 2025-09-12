from ...provider import PineconeProvider
from ...options import PineconeOptions
from ..indexer.index import PineconeIndex
from .....utils.preprocessor.chunker import Chunk
from pinecone import Pinecone 
from pinecone import IndexModel


class PineconeService: 
    __conn      : Pinecone
    __index     : IndexModel 
    options     : PineconeOptions 

    def __init__(self, options: PineconeOptions): 
        try: 
            self.__conn = PineconeProvider.get_connection()
            self.options = options

            # creating an index 
            created : bool = PineconeIndex.create_index(self.__conn, options)
            if not created: 
                raise Exception("could not create index")

            # storing index as a class private variable  
            self.__index = self.__conn.Index(options.index_name)

        except Exception as err: 
            raise err
    
    def upsert(self, records: list[Chunk], namespace: str = "chatbot") -> bool: 
        try: 
            self.__index.upsert_records(namespace, [chunk.model_dump_json() for chunk in records])
        except Exception as err: 
            raise err  
        
        