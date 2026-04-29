import requests
import yaml
from datetime import datetime

with open("config.yaml") as f:
    CFG = yaml.safe_load(f)

WEBHOOK = CFG.get("slack_webhook", "").strip()

def send_slack(msg):
    if not WEBHOOK:
        print("[Slack disabled]", msg)
        return

    try:
        requests.post(WEBHOOK, json={"text": msg}, timeout=5)
    except Exception as e:
        print("Slack error:", e)

def now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
