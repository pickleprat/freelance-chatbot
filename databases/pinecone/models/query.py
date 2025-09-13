from pydantic import BaseModel

class Query(BaseModel): 
    top_k       : int
    text        : str

class Field(BaseModel): 
    chunk_text  : str

class Hit(BaseModel): 
    _id          : str 
    _score       : float 
    fields       : Field

class QueryResult(BaseModel): 
    hits: list[Hit]


