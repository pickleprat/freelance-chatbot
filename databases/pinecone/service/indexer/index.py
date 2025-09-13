from databases.pinecone.models.options import PineconeOptions
from pinecone import Pinecone

class PineconeIndex: 
    @classmethod
    def create_index(cls, conn: Pinecone, options: PineconeOptions) -> bool : 
        try: 
            if options.name: 
                if not conn.has_index(options.name): 
                    conn.create_index_for_model(**options.model_dump())
                    return True 
                return False 
            else: 
                raise Exception("option needs to have index name")
        except Exception as error: 
            raise error
        




