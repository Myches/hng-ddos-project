import time
import statistics
from datetime import datetime
import state

def audit(msg):
    with open(state.AUDIT_LOG, "a") as f:
        f.write(msg + "\n")

def tick():
    now = int(time.time())

    if now != state.last_second_tick:
        state.per_second_counts.append(state.current_second_count)

        hour = datetime.utcnow().hour
        state.hourly_slots[hour].append(state.current_second_count)

        state.current_second_count = 0
        state.last_second_tick = now

def recalc():
    data = list(state.per_second_counts)

    if len(data) < 10:
        return

    state.baseline_mean = max(1.0, statistics.mean(data))

    if len(data) > 1:
        state.baseline_std = max(1.0, statistics.stdev(data))
    else:
        state.baseline_std = 1.0

    audit(
        f"[{datetime.utcnow()}] BASELINE RECALC | "
        f"mean={state.baseline_mean:.2f} "
        f"| std={state.baseline_std:.2f}"
    )

def run():
    last = time.time()

    while True:
        tick()

        if time.time() - last >= 60:
            recalc()
            last = time.time()

        time.sleep(1)
