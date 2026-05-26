import json
import os
import urllib.request
from datetime import date, timedelta
from typing import Optional


BASE_URL = "https://api.ouraring.com/v2/usercollection"


def fetch_score(endpoint: str, start_date: str, end_date: str, token: str) -> Optional[int]:
    url = f"{BASE_URL}/{endpoint}?start_date={start_date}&end_date={end_date}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read()).get("data", [])
    return data[-1]["score"] if data else None


def get_scores(token: str) -> dict:
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    return {
        "Sleep":     fetch_score("daily_sleep",     today,     today, token),
        "Readiness": fetch_score("daily_readiness", today,     today, token),
        "Activity":  fetch_score("daily_activity",  week_ago,  today, token),
    }


def format_message(scores: dict) -> str:
    today = date.today().isoformat()
    lines = [f"Oura scores for {today}"]
    for label, score in scores.items():
        lines.append(f"  {label:<10}{score if score is not None else 'N/A'}")
    return "\n".join(lines)


def main():
    from dotenv import load_dotenv
    load_dotenv()

    token = os.environ["OURA_API_KEY"]
    scores = get_scores(token)
    print(format_message(scores))


if __name__ == "__main__":
    main()
