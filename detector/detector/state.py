import time
from collections import defaultdict, deque

START_TIME = time.time()

# Sliding windows
ip_windows = defaultdict(deque)
global_window = deque()

# Counters
ip_totals = defaultdict(int)
ip_errors = defaultdict(int)

# Baseline
per_second_counts = deque(maxlen=1800)
baseline_mean = 1.0
baseline_std = 1.0
last_second_tick = int(time.time())
current_second_count = 0

# Hourly slots
hourly_slots = defaultdict(list)

# Ban state
banned_ips = {}  # ip -> metadata

AUDIT_LOG = "audit.log"
