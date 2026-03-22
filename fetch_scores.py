import os
from datetime import date
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.ouraring.com/v2/usercollection"
HEADERS = {"Authorization": f"Bearer {os.environ['OURA_API_KEY']}"}


def fetch_score(endpoint: str, start_date: str, end_date: str) -> Optional[int]:
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=HEADERS,
        params={"start_date": start_date, "end_date": end_date},
    )
    response.raise_for_status()
    data = response.json().get("data", [])
    return data[-1]["score"] if data else None


def main():
    today = date.today().isoformat()
    week_ago = date.fromordinal(date.today().toordinal() - 7).isoformat()

    sleep = fetch_score("daily_sleep", today, today)
    readiness = fetch_score("daily_readiness", today, today)
    activity = fetch_score("daily_activity", week_ago, today)

    print(f"Oura scores for {today}")
    print(f"  Sleep:     {sleep if sleep is not None else 'N/A'}")
    print(f"  Readiness: {readiness if readiness is not None else 'N/A'}")
    print(f"  Activity:  {activity if activity is not None else 'N/A'}")


if __name__ == "__main__":
    main()
