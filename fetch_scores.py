import base64
import json
import os
import urllib.request
from datetime import date, timedelta
from typing import Optional

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Created at module scope so the boto3 import + client setup is paid once during
# Lambda init rather than on every interaction (where we must return Discord's
# deferred ack within 3s). Guarded so local runs — which don't bundle boto3 —
# still import this module. Keys are never read from env vars; always from SSM.
try:
    import boto3
    _ssm = boto3.client("ssm", region_name="us-east-1")
    _lambda = boto3.client("lambda", region_name="us-east-1")
except ImportError:
    boto3 = _ssm = _lambda = None


BASE_URL = "https://api.ouraring.com/v2/usercollection"
DISCORD_API = "https://discord.com/api/v10"

# Discord's edge (Cloudflare) rejects the default Python-urllib agent with a 403,
# so every Discord request must send a descriptive User-Agent.
USER_AGENT = "oura-stats-texter (https://github.com/bfox1793/oura-stats-texter, 1.0)"


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
    """Post a standalone message to the channel via the incoming webhook (daily run)."""
    url = os.environ["DISCORD_WEBHOOK_URL"]
    payload = json.dumps({"content": message}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(f"Discord response: status={resp.status}")


# --- Discord slash-command (interaction) handling --------------------------

def _get_param(name: str, encrypted: bool = False) -> str:
    return _ssm.get_parameter(
        Name=f"/oura-stats-texter/{name}",
        WithDecryption=encrypted,
    )["Parameter"]["Value"]


def _verify_signature(event: dict, public_key: str) -> bool:
    """Verify the Ed25519 signature Discord attaches to every interaction request."""
    headers = event.get("headers") or {}
    signature = headers.get("x-signature-ed25519")
    timestamp = headers.get("x-signature-timestamp")
    if not signature or not timestamp:
        return False

    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()

    verify_key = VerifyKey(bytes.fromhex(public_key))
    try:
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        return True
    except BadSignatureError:
        return False


def _json_response(status: int, payload: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }


def _handle_interaction(event: dict, context) -> dict:
    # Only the public key is needed to ack the interaction — fetch just that one
    # param so the deferred reply goes out well within Discord's 3s window.
    if not _verify_signature(event, _get_param("discord_public_key")):
        return {"statusCode": 401, "body": "invalid request signature"}

    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()
    interaction = json.loads(body)

    # type 1 = PING (Discord's endpoint healthcheck / verification)
    if interaction.get("type") == 1:
        return _json_response(200, {"type": 1})

    # type 2 = APPLICATION_COMMAND (e.g. /oura). Defer immediately, then do the
    # real work in an async self-invocation so we never blow Discord's 3s budget.
    if interaction.get("type") == 2:
        _lambda.invoke(
            FunctionName=context.function_name,
            InvocationType="Event",
            Payload=json.dumps({
                "source": "oura-followup",
                "application_id": interaction["application_id"],
                "interaction_token": interaction["token"],
            }).encode(),
        )
        # type 5 = DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE ("thinking…")
        return _json_response(200, {"type": 5})

    return _json_response(400, {"error": "unhandled interaction type"})


def _run_followup(application_id: str, interaction_token: str) -> dict:
    """Async worker: fetch scores and edit the deferred interaction reply."""
    scores = get_scores(_get_param("oura_api_token", encrypted=True))
    message = format_message(scores)

    url = f"{DISCORD_API}/webhooks/{application_id}/{interaction_token}/messages/@original"
    payload = json.dumps({"content": message}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="PATCH",
    )
    with urllib.request.urlopen(req) as resp:
        print(f"Discord followup response: status={resp.status}")
    return {"statusCode": 200, "body": message}


def lambda_handler(event, context):
    # Async worker invocation (self-triggered from a slash command).
    if isinstance(event, dict) and event.get("source") == "oura-followup":
        return _run_followup(event["application_id"], event["interaction_token"])

    # HTTP request from Discord via the Lambda Function URL (latency-critical).
    if isinstance(event, dict) and "requestContext" in event and "http" in event.get("requestContext", {}):
        return _handle_interaction(event, context)

    # Scheduled daily run (EventBridge Scheduler) — post via the webhook.
    os.environ["DISCORD_WEBHOOK_URL"] = _get_param("discord_webhook_url", encrypted=True)
    scores = get_scores(_get_param("oura_api_token", encrypted=True))
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
