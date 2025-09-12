SELECT id, content, "lastUpdated"
FROM "PdfTextContent"
ORDER BY "lastUpdated" DESC
LIMIT %s;
