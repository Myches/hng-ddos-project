import time
import statistics
from datetime import datetime, timezone
import state


def audit(msg):
    with open(state.AUDIT_LOG, "a") as f:
        f.write(msg + "\n")


def tick():
    """Called every loop iteration — rolls per-second count into rolling windows."""
    now = int(time.time())

    if now != state.last_second_tick:
        count = state.current_second_count

        # Feed the 30-minute flat rolling window
        state.per_second_counts.append(count)

        # Feed the per-hour slot for the current UTC hour
        hour = datetime.now(timezone.utc).hour
        state.hourly_slots[hour].append(count)

        state.current_second_count = 0
        state.last_second_tick = now


def recalc():
    """
    Recalculate mean and stddev every 60 seconds.

    Strategy:
      1. Prefer the current hour's slot when it has >= 60 samples
         (at least one full minute of data), because recent per-hour
         traffic better represents the current baseline.
      2. Fall back to the full 30-minute rolling window otherwise.
    """
    hour = datetime.now(timezone.utc).hour
    hourly_data = list(state.hourly_slots[hour])

    # Use the hourly slot if it has enough data points
    if len(hourly_data) >= 60:
        data = hourly_data
        source = f"hourly(h={hour}, n={len(data)})"
    else:
        data = list(state.per_second_counts)
        source = f"rolling(n={len(data)})"

    if len(data) < 10:
        return  # Not enough data yet — keep existing baseline

    state.baseline_mean = max(1.0, statistics.mean(data))
    state.baseline_std = max(0.5, statistics.stdev(data) if len(data) > 1 else 1.0)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    audit(
        f"[{ts}] BASELINE RECALC | source={source} "
        f"| mean={state.baseline_mean:.2f} "
        f"| std={state.baseline_std:.2f}"
    )


def run():
    last_recalc = time.time()

    while True:
        tick()

        if time.time() - last_recalc >= 60:
            recalc()
            last_recalc = time.time()

        time.sleep(1)
