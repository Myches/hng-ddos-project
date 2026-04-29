import os
import json
import time
import yaml
import state
from detector import check_ip, check_global


with open("config.yaml") as f:
    CFG = yaml.safe_load(f)

LOG_FILE = CFG["log_file"]

def evict_old(now):
    while state.global_window and now - state.global_window[0] > 60:
        state.global_window.popleft()

    for ip in list(state.ip_windows.keys()):
        dq = state.ip_windows[ip]

        while dq and now - dq[0] > 60:
            dq.popleft()

        if not dq:
            del state.ip_windows[ip]

def process(line):
    try:
        data = json.loads(line.strip())
    except Exception:
        return

    ip = data.get("source_ip", "unknown")
    status = str(data.get("status", ""))

    now = time.time()

    state.ip_windows[ip].append(now)
    state.global_window.append(now)

    state.ip_totals[ip] += 1
    state.current_second_count += 1

    if status.startswith("4") or status.startswith("5"):
        state.ip_errors[ip] += 1

    evict_old(now)

    ip_rate = len(state.ip_windows[ip])
    global_rate = len(state.global_window)

    check_ip(ip, ip_rate)
    check_global(global_rate)

    print(
        f"[LIVE] {ip} | ip_rate={ip_rate} "
        f"| global_rate={global_rate}"
    )

def run():
    while not os.path.exists(LOG_FILE):
        print("Waiting for log file...")
        time.sleep(2)

    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()

            if not line:
                time.sleep(0.2)
                continue

            process(line)
