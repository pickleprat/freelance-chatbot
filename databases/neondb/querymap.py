from enum import Enum 

class PdfContentQuery(Enum): 
    getAllContent  = "./databases/neondb/sql/getallcontent.sql"
    getContentById = "./databases/neondb/sql/getcontentbyid.sql"

class QueryMap:
    PdfContent = PdfContentQuery
