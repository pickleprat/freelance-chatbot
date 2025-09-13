from pydantic import BaseModel

class FieldMap(BaseModel): 
    text: str 

class Embed(BaseModel): 
    model       : str       = "llama-text-embed-v2"
    field_map   : FieldMap  = FieldMap(text="chunk_text") 

class PineconeOptions(BaseModel): 
    name  : str
    cloud       : str   = "aws"
    region      : str   = "us-east-1"
    embed       : Embed = Embed()



