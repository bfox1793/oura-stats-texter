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

    return {
        "Sleep":     fetch_score("daily_sleep",     today, today, token),
        "Readiness": fetch_score("daily_readiness", today, today, token),
        "Activity":  (
            fetch_score("daily_activity", today, today, token)
            or fetch_score("daily_activity", (date.today() - timedelta(days=7)).isoformat(), today, token)
        ),
    }


def format_message(scores: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    score_lines = "\n".join(
        f"  {label:<10}{score if score is not None else 'N/A'}{'  👑' if score is not None and score >= 85 else ''}"
        for label, score in scores.items()
    )
    return f"Oura Scores for {today}\n```\n\n{score_lines}\n```"


def send_message(message: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    print(f"Telegram response: message_id={result['result']['message_id']}")


def lambda_handler(event, context):
    import boto3

    ssm = boto3.client("ssm", region_name="us-east-1")

    def get_param(name, encrypted=False):
        return ssm.get_parameter(
            Name=f"/oura-stats-texter/{name}",
            WithDecryption=encrypted,
        )["Parameter"]["Value"]

    os.environ["OURA_API_KEY"]        = get_param("oura_api_token", encrypted=True)
    os.environ["TELEGRAM_BOT_TOKEN"]  = get_param("telegram_bot_token", encrypted=True)
    os.environ["TELEGRAM_CHAT_ID"]    = get_param("telegram_chat_id")

    scores = get_scores(os.environ["OURA_API_KEY"])
    message = format_message(scores)
    send_message(message)

    return {"statusCode": 200, "body": message}


def main():
    from dotenv import load_dotenv
    load_dotenv()

    token = os.environ["OURA_API_KEY"]
    scores = get_scores(token)
    message = format_message(scores)
    print(message)
    send_message(message)


if __name__ == "__main__":
    main()
