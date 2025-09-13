from databases.pinecone.provider import PineconeProvider
from databases.pinecone.models.options import PineconeOptions
from databases.pinecone.models.query import Query, QueryResult, Hit, Field
from databases.pinecone.service.indexer.index import PineconeIndex
from utils.preprocessor.chunker import Chunk
from config.chatbot import Config 
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
                print("index already exists")

            # storing index as a class private variable  
            self.__index = self.__conn.Index(options.name)

        except Exception as err: 
            raise err
    
    def upsert(self, records: list[Chunk]) -> bool: 
        try: 
            # upserting records to remote pinecone 
            self.__index.upsert_records(Config.NAMESPACE, [chunk.model_dump(by_alias=True) for chunk in records])
        except Exception as err: 
            raise err  

    def fetch(self, query: Query) -> list[QueryResult]: 
        try: 
            results = self.__index.search(
                Config.NAMESPACE, 
                query = query.model_dump_json(), 
            )

            return QueryResult(hits=[Hit(
                _id=hit["_id"], 
                _score=hit["_score"], 
                fields=Field(chunk_text=hit["chunk_text"]), 
            ) for hit in results["result"]["hits"]])

        except Exception as error: 
            raise error 

    def stats(self): 
        pass 
        
        