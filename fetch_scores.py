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


# --- Lambda entrypoint ---

def lambda_handler(event, context):
    import boto3

    ssm = boto3.client("ssm", region_name="us-east-1")

    token = ssm.get_parameter(
        Name="/oura-stats-texter/oura_api_token",
        WithDecryption=True,
    )["Parameter"]["Value"]

    sms_gateway_email = ssm.get_parameter(
        Name="/oura-stats-texter/sms_gateway_email",
    )["Parameter"]["Value"]

    sender_email = ssm.get_parameter(
        Name="/oura-stats-texter/sender_email",
    )["Parameter"]["Value"]

    scores = get_scores(token)
    message = format_message(scores)

    boto3.client("ses", region_name="us-east-1").send_email(
        Source=sender_email,
        Destination={"ToAddresses": [sms_gateway_email]},
        Message={
            "Subject": {"Data": "Oura Scores"},
            "Body": {"Text": {"Data": message}},
        },
    )

    return {"statusCode": 200, "body": message}


# --- Local entrypoint ---

def main():
    from dotenv import load_dotenv
    load_dotenv()

    token = os.environ["OURA_API_KEY"]
    scores = get_scores(token)
    print(format_message(scores))


if __name__ == "__main__":
    main()
