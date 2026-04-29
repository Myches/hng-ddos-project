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

        for ip, meta in list(state.banned_ips.items()):
            exp = meta.get("expires_at")

            if exp is not None and current >= exp:
                # Remove iptables rule
                subprocess.run(
                    ["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"],
                    check=False
                )

                condition = meta.get("reason", "unknown")
                duration = meta.get("duration", "?")
                rate = meta.get("rate", "?")
                baseline = meta.get("baseline", "?")
                human = f"{duration}s" if isinstance(duration, int) else str(duration)

                send_slack(
                    f"✅ UNBAN {ip}\n"
                    f"Condition: {condition}\n"
                    f"Rate at ban: {rate}\n"
                    f"Baseline at ban: {baseline}\n"
                    f"Duration served: {human}\n"
                    f"Time: {now()}"
                )

                audit(
                    f"[{now()}] UNBAN {ip} | condition={condition} | rate={rate} | baseline={baseline} | duration={human}"
                )

                to_remove.append(ip)

        for ip in to_remove:
            del state.banned_ips[ip]

        time.sleep(30)
