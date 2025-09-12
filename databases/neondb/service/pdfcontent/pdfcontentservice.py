from ...provider import NeonProvider
from ...querymap import QueryMap
from ...sql.loader import load_sql
from .model import PdfContent

class PDFContentService:
    def __init__(self):
        self.conn = NeonProvider.get_connection()

    def get_all_content(self, limit: int = 10) -> list[PdfContent]:
        sql = load_sql(QueryMap.PdfContent.getAllContent.value)
        with self.conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
            return [PdfContent(**dict(row)) for row in rows]  

    def get_content_by_id(self, content_id: str) -> PdfContent | None:
        sql = load_sql(QueryMap.PdfContent.getContentById.value)
        with self.conn.cursor() as cur:
            cur.execute(sql, (content_id,))
            row = cur.fetchone()
            return PdfContent(**dict(row)) if row else None  
