import sqlite3

DB_NAME = "codegene.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS databases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        database_id INTEGER,
        name TEXT
    );

    CREATE TABLE IF NOT EXISTS enums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        database_id INTEGER,
        name TEXT
    );

    CREATE TABLE IF NOT EXISTS enum_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enum_id INTEGER,
        value TEXT
    );

    CREATE TABLE IF NOT EXISTS fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        name TEXT,
        type TEXT,
        nullable INTEGER DEFAULT 0,
        enum_id INTEGER
    );
    """)
    conn.close()