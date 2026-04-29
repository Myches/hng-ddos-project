import subprocess
import time
import yaml
import state
from notifier import send_slack, now

with open("config.yaml") as f:
    CFG = yaml.safe_load(f)

BAN_SCHEDULE = CFG["ban_schedule"]


def get_duration(strikes):
    """Return ban duration in seconds, or None for permanent."""
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
        return  # Already banned — don't double-ban

    # Increment the persistent lifetime strike counter
    state.ban_history[ip] += 1
    strikes = state.ban_history[ip]

    duration = get_duration(strikes)
    expires_at = None if duration is None else time.time() + duration
    human = "permanent" if duration is None else f"{duration}s"

    # Apply iptables DROP rule
    try:
        subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            check=False
        )
    except Exception:
        pass

    state.banned_ips[ip] = {
        "ip": ip,
        "strikes": strikes,
        "duration": duration,
        "expires_at": expires_at,
        "reason": condition,
        "rate": rate,
        "baseline": baseline,
    }

    send_slack(
        f"🚫 BAN {ip}\n"
        f"Condition: {condition}\n"
        f"Rate: {rate}\n"
        f"Baseline: {baseline:.2f}\n"
        f"Duration: {human}\n"
        f"Strike: {strikes}\n"
        f"Time: {now()}"
    )

    audit(
        f"[{now()}] BAN {ip} | {condition} | rate={rate} | baseline={baseline:.2f} | duration={human} | strike={strikes}"
    )
