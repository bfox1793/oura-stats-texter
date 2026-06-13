"""One-time registration of the /oura slash command.

Run locally after creating your Discord application:

    DISCORD_APP_ID=...  DISCORD_BOT_TOKEN=...  python register_command.py

Requires (only for registration):
  - DISCORD_APP_ID    : Application ID (Discord developer portal → General Info)
  - DISCORD_BOT_TOKEN : Bot token       (Discord developer portal → Bot)

Global commands can take up to ~1 hour to propagate the first time.
"""

import json
import os
import urllib.request


def main():
    from dotenv import load_dotenv
    load_dotenv()

    app_id = os.environ["DISCORD_APP_ID"]
    bot_token = os.environ["DISCORD_BOT_TOKEN"]
    guild_id = os.environ.get("DISCORD_GUILD_ID")

    command = {
        "name": "oura",
        "description": "Fetch today's Oura scores and post them now",
        "type": 1,  # CHAT_INPUT
    }

    # Guild-scoped commands register instantly; global ones take up to ~1 hour.
    if guild_id:
        url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands"
    else:
        url = f"https://discord.com/api/v10/applications/{app_id}/commands"
    req = urllib.request.Request(
        url,
        data=json.dumps(command).encode(),
        headers={
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
            # Discord's edge (Cloudflare) rejects the default Python-urllib agent.
            "User-Agent": "oura-stats-texter (https://github.com/bfox1793/oura-stats-texter, 1.0)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}")
        raise
    print(f"Registered /{result['name']} (id={result['id']})")


if __name__ == "__main__":
    main()
