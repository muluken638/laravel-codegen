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

def update_field(field_id, name, field_type, nullable=0, enum_id=None):
    
    conn = get_connection()

    conn.execute("""
                 Update fields set name=?, type=?, nullable=?, enum_id=? where id=? """, (name, field_type, nullable, enum_id, field_id))
    conn.commit()
    conn.close()

def delete_field(field_id):
    conn= get_connection()
    conn.execute("""
                 Delete from fields where id=? """, (field_id,))
    conn.commit()
    conn.close()