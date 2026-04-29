import time
import subprocess
import state
from notifier import send_slack, now

def audit(msg):
    with open(state.AUDIT_LOG, "a") as f:
        f.write(msg + "\n")

def run():
    while True:
        current = time.time()
        to_remove = []

        for ip, meta in state.banned_ips.items():
            exp = meta["expires_at"]

            if exp is not None and current >= exp:
                subprocess.run(
                    ["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"],
                    check=False
                )
                send_slack(f"✅ UNBAN {ip} | Time: {now()}")
                audit(f"[{now()}] UNBAN {ip} | expired")
                to_remove.append(ip)

        for ip in to_remove:
            del state.banned_ips[ip]

        time.sleep(30)
