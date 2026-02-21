from database.database import get_connection


def create_field(table_id, name, field_type, nullable=0, enum_id=None):

    conn = get_connection()

    conn.execute("""
        INSERT INTO fields (table_id, name, type, nullable, enum_id)
        VALUES (?, ?, ?, ?, ?)
    """, (table_id, name, field_type, nullable, enum_id))

    conn.commit()
    conn.close()


def get_fields(table_id):

    conn = get_connection()

    rows = conn.execute("""
        SELECT id, name, type, nullable, enum_id
        FROM fields
        WHERE table_id=?
    """, (table_id,)).fetchall()

    conn.close()

    return rows