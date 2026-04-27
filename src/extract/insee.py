import requests
import json
import time
import xml.etree.ElementTree as ET

BASE_URL = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM"

SERIES = {
    "001763852": "ipc_france",          # Monthly CPI, Base 2015, all households
    "001688526": "unemployment_france", # BIT unemployment rate, metropolitan France
}

DATE_START = "2015-01"
DATE_END   = "2025-12"


def fetch_with_retry(url: str, params: dict, max_retries: int = 3) -> str:
    """
    Fetches a URL and returns the raw response text.
    Retries with exponential backoff on transient failures.

    Args:
        url: Target endpoint.
        params: Query string parameters.
        max_retries: Maximum number of attempts before raising.

    Returns:
        Raw response text.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"Attempt {attempt + 1} failed ({e}). Retrying in {wait}s...")
            time.sleep(wait)


def fetch_series(id_bank: str) -> list:
    """
    Fetches all observations for a given INSEE idBank series.
    Parses the SDMX-XML response into a flat list of records.

    Args:
        id_bank: INSEE series identifier (idBank).

    Returns:
        List of dicts with keys: id_bank, series, period, value.
    """
    url = f"{BASE_URL}/{id_bank}"
    params = {
        "startPeriod": DATE_START,
        "endPeriod":   DATE_END,
    }

    xml_text = fetch_with_retry(url, params)
    root = ET.fromstring(xml_text)

    entries = []

    # Primary parse: SDMX structurespecific namespace
    sdmx_ns = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific"
    for obs in root.iter(f"{{{sdmx_ns}}}Obs"):
        period = obs.get("TIME_PERIOD")
        value  = obs.get("OBS_VALUE")
        if period and value:
            entries.append({
                "id_bank": id_bank,
                "series":  SERIES.get(id_bank, id_bank),
                "period":  period,
                "value":   float(value),
            })

    # Fallback: namespace-free Obs elements
    if not entries:
        for obs in root.iter("Obs"):
            period = obs.get("TIME_PERIOD")
            value  = obs.get("OBS_VALUE")
            if period and value:
                entries.append({
                    "id_bank": id_bank,
                    "series":  SERIES.get(id_bank, id_bank),
                    "period":  period,
                    "value":   float(value),
                })

    print(f"{SERIES.get(id_bank, id_bank)}: {len(entries)} observations")
    return entries


def save_raw(data: list, filename: str) -> None:
    """Serializes data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    all_data = []
    for id_bank in SERIES:
        all_data.extend(fetch_series(id_bank))
    save_raw(all_data, "data/insee_raw.json")
    print(f"\n{len(all_data)} total rows saved → data/insee_raw.json")