import os 

def load_sql(path: str) -> str:
    """Load SQL file from disk"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"SQL file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()