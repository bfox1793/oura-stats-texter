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


def send_sms(message: str) -> None:
    from twilio.rest import Client

    client = Client(
        username=os.environ["TWILIO_API_KEY_SID"],
        password=os.environ["TWILIO_API_KEY_SECRET"],
        account_sid=os.environ["TWILIO_ACCOUNT_SID"],
    )
    response = client.messages.create(
        to=os.environ["RECIPIENT_PHONE_NUMBER"],
        from_=os.environ["TWILIO_PHONE_NUMBER"],
        body=message,
    )
    print(f"Twilio response: sid={response.sid} status={response.status}")


def lambda_handler(event, context):
    import boto3

    ssm = boto3.client("ssm", region_name="us-east-1")

    def get_param(name, encrypted=False):
        return ssm.get_parameter(
            Name=f"/oura-stats-texter/{name}",
            WithDecryption=encrypted,
        )["Parameter"]["Value"]

    os.environ["OURA_API_KEY"]           = get_param("oura_api_token", encrypted=True)
    os.environ["TWILIO_ACCOUNT_SID"]     = get_param("twilio_account_sid", encrypted=True)
    os.environ["TWILIO_API_KEY_SID"]     = get_param("twilio_api_key_sid", encrypted=True)
    os.environ["TWILIO_API_KEY_SECRET"]  = get_param("twilio_api_key_secret", encrypted=True)
    os.environ["TWILIO_PHONE_NUMBER"]    = get_param("twilio_phone_number")
    os.environ["RECIPIENT_PHONE_NUMBER"] = get_param("recipient_phone_number")

    scores = get_scores(os.environ["OURA_API_KEY"])
    message = format_message(scores)
    send_sms(message)

    return {"statusCode": 200, "body": message}


def main():
    from dotenv import load_dotenv
    load_dotenv()

    token = os.environ["OURA_API_KEY"]
    scores = get_scores(token)
    message = format_message(scores)
    print(message)
    send_sms(message)


if __name__ == "__main__":
    main()
