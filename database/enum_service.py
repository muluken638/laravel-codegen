from database.database import get_connection


def create_enum(database_id, name):

    conn = get_connection()

    conn.execute(
        "INSERT INTO enums (database_id, name) VALUES (?,?)",
        (database_id, name)
    )

    conn.commit()
    conn.close()


def get_enums(database_id):

    conn = get_connection()

    rows = conn.execute(
        "SELECT id, name FROM enums WHERE database_id=?",
        (database_id,)
    ).fetchall()

    conn.close()

    return rows


def add_enum_value(enum_id, value):

    conn = get_connection()

    conn.execute(
        "INSERT INTO enum_values (enum_id,value) VALUES (?,?)",
        (enum_id, value)
    )

    conn.commit()
    conn.close()


def get_enum_values(enum_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, value FROM enum_values WHERE enum_id=?", (enum_id,)
    ).fetchall()
    conn.close()
    # Assign numeric codes starting from 100
    return [{"name": r[1], "value": 100 + r[0]} for r in rows]