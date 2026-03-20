"""
SQLite database connection and schema initialization.

Uses aiosqlite for async operations. The schema is designed to be
Oracle-compatible — avoid SQLite-specific functions.
"""

import aiosqlite
import os

DATABASE_PATH = os.getenv("DATABASE_PATH", "configs.db")

# Oracle equivalent: Use sequences + triggers instead of AUTOINCREMENT.
# Oracle equivalent: Use VARCHAR2 instead of TEXT, NUMBER instead of INTEGER.
# Oracle equivalent: Use SYSTIMESTAMP instead of CURRENT_TIMESTAMP.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    environment TEXT NOT NULL CHECK(environment IN ('dev', 'staging', 'prod')),
    config_key TEXT NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_name, environment, config_key)
);
"""


async def get_db() -> aiosqlite.Connection:
    """Open a new database connection with row factory enabled."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Create the configurations table if it doesn't exist."""
    db = await get_db()
    try:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()
    finally:
        await db.close()
