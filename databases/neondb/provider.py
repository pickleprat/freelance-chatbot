import psycopg2
from psycopg2.extras import RealDictCursor
from config.chatbot import Config

class NeonProvider:
    _conn = None

    @classmethod
    def get_connection(cls):
        if cls._conn is None or cls._conn.closed:
            cls._conn = psycopg2.connect(
                Config.NEON_CONNECTION_STRING,
                cursor_factory=RealDictCursor
            )
        return cls._conn
