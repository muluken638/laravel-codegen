from database.database import get_connection

def to_snake_case(name):
    """Convert 'Table Name' → 'table_name'"""
    return "_".join(name.strip().lower().split())
def create_table(database_id, name):

    conn = get_connection()

    conn.execute(
        "INSERT INTO tables (database_id, name) VALUES (?,?)",
        (database_id, name)
    )

    conn.commit()
    conn.close()


def get_tables(database_id):

    conn = get_connection()

    rows = conn.execute(
        "SELECT id, name FROM tables WHERE database_id=?",
        (database_id,)
    ).fetchall()

    conn.close()

    return rows