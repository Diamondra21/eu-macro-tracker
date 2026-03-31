import requests, json, time

BASE_URL = "https://api.worldbank.org/v2/country"
DATE_RANGE = "2015:2025"
PER_PAGE = 50

COUNTRIES = ["FRA", "DEU", "ESP", "EUU"]

INDICATORS = {
    "NY.GDP.MKTP.CD":    "gdp",
    "FP.CPI.TOTL.ZG":   "inflation",
    "SL.UEM.TOTL.ZS":   "unemployment",
    "GC.DOD.TOTL.GD.ZS": "public_debt",
}

def fetch_indicator(country: str, indicator: str) -> list:
    """
    Fetches all entries for a given country and indicator.
    Handles pagination automatically.
    Returns a flat list of dicts, one entry per year.
    """

    url = f"{BASE_URL}/{country}/indicator/{indicator}"
    all_entries = []
    page = 1
    while True:
        try:
            params = {"format": "json", "per_page": PER_PAGE, "page": page, "date": DATE_RANGE}
            data = fetch_with_retry(url, params)
            entries = data[1] or []           # entries for this page or empty list for None answer
            all_entries.extend(entries) # accumulate all entries
            print(f"{country} / {INDICATORS[indicator]} : {len(entries)} rows")
            if page >= data[0]["pages"]: # last page reached
                break
            page += 1

        except requests.exceptions.Timeout:
            print("Timeout — API doesn't answer")
            raise
        except requests.exceptions.HTTPError as e:
            print(f"HTTP ERROR: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Network error : {e}")
            raise

        

    return all_entries
        

def save_raw(data: list, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_with_retry(url: str, params: dict, max_retries: int = 3) -> dict:
    """Calls the URL with exponential backoff retry on failure."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url = url, 
                                    params=params, 
                                    timeout=30 )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise  # last attempt — give up and raise the error
            wait = 2 ** attempt  # 1s, 2s, 4s — exponential backoff
            print(f"Attempt {attempt + 1} failed. Retrying in {wait}s...")
            time.sleep(wait)

if __name__ == "__main__":
    data = []
    for country in COUNTRIES:
        for indicator in INDICATORS:
            data.extend(fetch_indicator(country, indicator))
    save_raw(data, "data/worldbank_raw.json")

    print(f"{len(data)} rows saved")