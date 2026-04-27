import json
from database import get_connection


def load_worldbank(filepath: str) -> None:
    """
    Loads WorldBank raw JSON into stg_worldbank_raw.
    Idempotent: skips duplicate (country_code, indicator_code, year) rows.

    Args:
        filepath: Path to the worldbank raw JSON file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        records = json.load(f)

    rows = []
    for r in records:
        if r.get("value") is None:
            continue
        rows.append((
            r["countryiso3code"],
            r["indicator"]["id"],
            r["indicator"]["value"],
            int(r["date"]),
            float(r["value"]),
        ))

    sql = """
        INSERT INTO stg_worldbank_raw
            (country_code, indicator_code, indicator_name, year, value)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (country_code, indicator_code, year) DO NOTHING
    """

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.executemany(sql, rows)
        print(f"WorldBank: {len(rows)} rows inserted (duplicates skipped)")
    finally:
        conn.close()


def load_insee(filepath: str) -> None:
    """
    Loads INSEE raw JSON into stg_insee_raw.
    Idempotent: skips duplicate (id_bank, period) rows.

    Args:
        filepath: Path to the INSEE raw JSON file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        records = json.load(f)

    rows = [
        (r["id_bank"], r["series"], r["period"], float(r["value"]))
        for r in records
        if r.get("value") is not None
    ]

    sql = """
        INSERT INTO stg_insee_raw
            (id_bank, series, period, value)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_bank, period) DO NOTHING
    """

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.executemany(sql, rows)
        print(f"INSEE: {len(rows)} rows inserted (duplicates skipped)")
    finally:
        conn.close()


if __name__ == "__main__":
    load_worldbank("data/worldbank_raw.json")
    load_insee("data/insee_raw.json")