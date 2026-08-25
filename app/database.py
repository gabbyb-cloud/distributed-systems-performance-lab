import psycopg

DATABASE_URL = "postgresql://labuser:labpassword@localhost:5432/performance_lab"


def fetch_item(item_id: int):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name FROM items WHERE id = %s",
                (item_id,),
            )
            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "item_id": row[0],
        "name": row[1],
        "source": "postgresql",
    }
