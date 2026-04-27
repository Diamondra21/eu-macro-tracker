import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src", "load"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "extract"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "transform"))

from worldbank import fetch_indicator, save_raw, COUNTRIES, INDICATORS
from insee import fetch_series, save_raw as save_raw_insee, SERIES
from staging import load_worldbank, load_insee
from run_sql import run_transforms
from database import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def extract() -> None:
    """Extracts data from WorldBank and INSEE APIs and saves to local JSON files."""
    logger.info("--- EXTRACT ---")

    wb_data = []
    for country in COUNTRIES:
        for indicator in INDICATORS:
            wb_data.extend(fetch_indicator(country, indicator))
    save_raw(wb_data, "data/worldbank_raw.json")
    logger.info(f"WorldBank: {len(wb_data)} rows saved")

    insee_data = []
    for id_bank in SERIES:
        insee_data.extend(fetch_series(id_bank))
    save_raw_insee(insee_data, "data/insee_raw.json")
    logger.info(f"INSEE: {len(insee_data)} rows saved")


def load() -> None:
    """Loads raw JSON files into staging tables."""
    logger.info("--- LOAD ---")
    load_worldbank("data/worldbank_raw.json")
    load_insee("data/insee_raw.json")


def transform() -> None:
    """Runs SQL transformations from staging to star schema."""
    logger.info("--- TRANSFORM ---")
    run_transforms()


def validate() -> None:
    """
    Runs basic row count checks on final tables.
    Raises RuntimeError if any table is empty.
    """
    logger.info("--- VALIDATE ---")
    checks = [
        ("dim_country",   "SELECT COUNT(*) FROM dim_country"),
        ("dim_indicator", "SELECT COUNT(*) FROM dim_indicator"),
        ("dim_time",      "SELECT COUNT(*) FROM dim_time"),
        ("fact_indicators", "SELECT COUNT(*) FROM fact_indicators"),
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for table, query in checks:
                cur.execute(query)
                count = cur.fetchone()[0]
                if count == 0:
                    raise RuntimeError(f"Validation failed: {table} is empty")
                logger.info(f"{table}: {count} rows ✓")
    finally:
        conn.close()


if __name__ == "__main__":
    logger.info("Pipeline started")
    try:
        extract()
        load()
        transform()
        validate()
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)