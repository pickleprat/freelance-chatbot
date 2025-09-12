from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PdfContent(BaseModel):
    id: UUID
    content: str
    lastUpdated: datetime
