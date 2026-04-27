import os
import psycopg2
from psycopg2.extensions import connection as PgConnection
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> PgConnection:
    """
    Creates and returns a PostgreSQL connection using environment variables.

    Expected .env keys:
        DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

    Returns:
        An open psycopg2 connection.

    Raises:
        psycopg2.OperationalError: If the connection cannot be established.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def run_sql_file(filepath: str) -> None:
    """
    Executes a SQL file against the database.
    Commits on success, rolls back on error.

    Args:
        filepath: Path to the .sql file to execute.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        print(f"Executed: {filepath}")
    except Exception as e:
        print(f"Error executing {filepath}: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_sql_file("sql/create_tables.sql")
    print("All tables created successfully.")