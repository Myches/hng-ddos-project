import os
import requests
import yaml
from datetime import datetime, timezone

with open("config.yaml") as f:
    CFG = yaml.safe_load(f)

# Prefer the environment variable — fall back to config.yaml value.
# Never commit the real webhook URL; set SLACK_WEBHOOK in your shell or
# docker-compose environment instead.
WEBHOOK = (os.environ.get("SLACK_WEBHOOK") or CFG.get("slack_webhook", "")).strip()

def send_slack(msg):
    if not WEBHOOK:
        print("[Slack disabled — set SLACK_WEBHOOK env var]", msg)
        return
    try:
        requests.post(WEBHOOK, json={"text": msg}, timeout=5)
    except Exception as e:
        print("Slack error:", e)

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
