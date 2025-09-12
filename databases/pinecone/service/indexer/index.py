from ...options import PineconeOptions
from pinecone import Pinecone

class PineconeIndex: 
    @classmethod
    def create_index(cls, conn: Pinecone, options: PineconeOptions) -> bool : 
        try: 
            if options.index_name: 
                conn.create_index(**options.model_dump_json())
                return True 
            else: 
                raise Exception("option needs to have index name")
        except Exception as error: 
            raise error
        




