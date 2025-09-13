from pydantic import BaseModel, Field

class Chunk(BaseModel):
    id: str = Field(..., alias="_id")
    chunk_text: str

    class Config:
        populate_by_name = True
        validate_by_name = True