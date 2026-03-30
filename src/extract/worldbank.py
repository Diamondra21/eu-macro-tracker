import requests, json

BASE_URL = "https://api.worldbank.org/v2/country/"
COUNTRY_CODE = "FRA"
INDICATOR_CODE = "NY.GDP.MKTP.CD"
DATE_RANGE = "2015:2024"

def fetch_indicator(country: str, indicator: str, date_range: str) -> list:
    """Function to call WorldBank API"""
    url = f"{BASE_URL}/{country}/indicator/{indicator}"
    try:
        response = requests.get(url = BASE_URL, 
                                params={"format": "json", "per_page": 10, "date": DATE_RANGE}, 
                                timeout=30 )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print("Timeout — API doesn't answer")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"HTTP ERROR: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Network error : {e}")
        raise

    return data[1]
        

def save_raw(data: list, filename: str) -> None:
    with open("data/worldbank_raw.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    data = fetch_indicator(COUNTRY_CODE, INDICATOR_CODE, DATE_RANGE)
    save_raw(data, "worldbank_raw_json")

    print(f"{len(data)} rows saved")