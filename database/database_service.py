from database.database import get_connection


def create_database(name):

    conn = get_connection()

    conn.execute(
        "INSERT INTO databases (name) VALUES (?)",
        (name,)
    )

    conn.commit()
    conn.close()


def get_databases():

    conn = get_connection()

    rows = conn.execute(
        "SELECT id, name FROM databases"
    ).fetchall()

    conn.close()

    return rows