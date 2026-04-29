import state
from blocker import ban_ip
from notifier import send_slack, now

def check_ip(ip, rate):
    mean = state.baseline_mean
    std = state.baseline_std

    errors = state.ip_errors[ip]
    z_limit = 3.0

    if errors > mean * 3:
        z_limit = 2.0

    z = (rate - mean) / std

    if z > z_limit or rate > mean * 5:
        ban_ip(ip, "Per-IP anomaly", rate, mean)

def check_global(rate):
    mean = state.baseline_mean
    std = state.baseline_std

    z = (rate - mean) / std

    if z > 3 or rate > mean * 5:
        send_slack(
            f"🌍 GLOBAL ALERT\n"
            f"Rate: {rate}\n"
            f"Baseline: {mean:.2f}\n"
            f"Time: {now()}"
        )
