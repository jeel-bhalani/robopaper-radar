from pathlib import Path
from db import get_connection

SCHEMA_FILE = Path(__file__).parent.parent / "sql" / "schema.sql"

with get_connection() as conn:
    conn.execute(SCHEMA_FILE.read_text())

print("Tables created ✅")