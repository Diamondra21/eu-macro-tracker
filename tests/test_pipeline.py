import json
import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "load"))
from database import get_connection


# =============================================================
# Fixtures
# =============================================================

@pytest.fixture
def db_conn():
    """Opens a database connection and closes it after the test."""
    conn = get_connection()
    yield conn
    conn.close()


@pytest.fixture
def worldbank_data():
    """Loads the WorldBank raw JSON file."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "worldbank_raw.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def insee_data():
    """Loads the INSEE raw JSON file."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "insee_raw.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================
# Tests — raw data integrity
# =============================================================

def test_worldbank_raw_not_empty(worldbank_data):
    """WorldBank JSON must contain at least one record."""
    assert len(worldbank_data) > 0


def test_worldbank_raw_required_keys(worldbank_data):
    """Each WorldBank record must have the expected keys."""
    required = {"countryiso3code", "indicator", "date", "value"}
    for record in worldbank_data[:10]:
        assert required.issubset(record.keys())


def test_worldbank_all_countries_present(worldbank_data):
    """All four expected country codes must appear in the data."""
    countries = {r["countryiso3code"] for r in worldbank_data}
    assert {"FRA", "DEU", "ESP", "EUU"}.issubset(countries)


def test_insee_raw_not_empty(insee_data):
    """INSEE JSON must contain at least one record."""
    assert len(insee_data) > 0


def test_insee_raw_required_keys(insee_data):
    """Each INSEE record must have the expected keys."""
    required = {"id_bank", "series", "period", "value"}
    for record in insee_data[:10]:
        assert required.issubset(record.keys())


# =============================================================
# Tests — database
# =============================================================

def test_fact_indicators_not_empty(db_conn):
    """fact_indicators must contain rows after pipeline run."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM fact_indicators")
        count = cur.fetchone()[0]
    assert count > 0


def test_dim_country_has_four_entries(db_conn):
    """dim_country must contain exactly 4 countries."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM dim_country")
        count = cur.fetchone()[0]
    assert count == 4


def test_no_null_values_in_fact_country(db_conn):
    """fact_indicators must have no NULL country_id."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM fact_indicators WHERE country_id IS NULL")
        count = cur.fetchone()[0]
    assert count == 0