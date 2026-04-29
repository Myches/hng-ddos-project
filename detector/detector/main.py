import threading
import time

import monitor
import baseline
import unbanner
import dashboard

def main():
    threads = [
        threading.Thread(target=monitor.run, daemon=True),
        threading.Thread(target=baseline.run, daemon=True),
        threading.Thread(target=unbanner.run, daemon=True),
        threading.Thread(target=dashboard.run, daemon=True),
    ]

    for t in threads:
        t.start()

    print("Detector running...")

    while True:
        time.sleep(5)

if __name__ == "__main__":
    main()
