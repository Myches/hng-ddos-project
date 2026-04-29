import subprocess
import time
import yaml
import state
from notifier import send_slack, now

with open("config.yaml") as f:
    CFG = yaml.safe_load(f)

BAN_SCHEDULE = CFG["ban_schedule"]

def get_duration(strikes):
    idx = min(strikes - 1, len(BAN_SCHEDULE) - 1)
    val = BAN_SCHEDULE[idx]
    if val == "permanent":
        return None
    return int(val)

def audit(msg):
    with open(state.AUDIT_LOG, "a") as f:
        f.write(msg + "\n")

def ban_ip(ip, condition, rate, baseline):
    if ip in state.banned_ips:
        return

    previous = 0
    for _, meta in state.banned_ips.items():
        if meta.get("ip") == ip:
            previous = meta.get("strikes", 0)

    strikes = previous + 1
    duration = get_duration(strikes)

    try:
        subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            check=False
        )
    except Exception:
        pass

    expires_at = None if duration is None else time.time() + duration

    state.banned_ips[ip] = {
        "ip": ip,
        "strikes": strikes,
        "duration": duration,
        "expires_at": expires_at,
        "reason": condition
    }

    human = "permanent" if duration is None else f"{duration}s"

    send_slack(
        f"🚫 BAN {ip}\n"
        f"Condition: {condition}\n"
        f"Rate: {rate}\n"
        f"Baseline: {baseline}\n"
        f"Duration: {human}\n"
        f"Time: {now()}"
    )

    audit(
        f"[{now()}] BAN {ip} | {condition} | {rate} | {baseline} | {human}"
    )
