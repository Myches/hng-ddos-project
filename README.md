# HNG Stage 3 Task — Real-Time Anomaly Detection Engine / DDoS Detection Tool

## Project Overview

This project is a real-time anomaly detection and automated response engine built to protect a public-facing cloud storage platform powered by Nextcloud.

The system continuously monitors incoming HTTP traffic from Nginx access logs, learns what normal traffic looks like over time, detects suspicious spikes or abusive behavior, and automatically responds by:

- Sending Slack alerts
- Blocking malicious IPs with iptables
- Releasing bans automatically on schedule
- Displaying live metrics on a dashboard

This helps reduce the impact of DDoS attacks, brute-force attempts, traffic floods, and unexpected request surges.

---

## Live Deployment Details

### Public Server IP

```text
http://184.73.41.83
Live Metrics Dashboard
http://184.73.41.83:5000

Keep the server online during grading.

Tech Stack
Language Used: Python

I chose Python because it provides:

Fast development speed
Strong standard libraries
Excellent support for threading
Easy HTTP integrations
Clean and readable syntax
Great fit for security tooling
Infrastructure Architecture
Internet Traffic
      ↓
   Nginx Reverse Proxy
(JSON Access Logs Enabled)
      ↓
Shared Docker Volume
(HNG-nginx-logs)
      ↓
Python Detection Daemon
      ↓
 ┌──────────────┬──────────────┬──────────────┐
 │              │              │
Slack Alerts   iptables      Dashboard
              Blocking       Flask UI
Features Implemented
1. Real-Time Log Monitoring

The daemon continuously tails:

/var/log/nginx/hng-access.log

Each JSON log line contains:

source_ip
timestamp
method
path
status
response_size
2. Sliding Window Detection (Deque Based)

Two sliding windows are maintained for the last 60 seconds.

Per-IP Window

Tracks requests sent by each IP over the last 60 seconds.

Global Window

Tracks all requests hitting the server over the last 60 seconds.

Why deque?

Python deque gives:

Fast append
Fast removal
Efficient real-time updates
Eviction Logic

Every request:

Add current timestamp
Remove entries older than 60 seconds
Queue length = live request rate
3. Rolling Baseline Engine

The system learns normal traffic automatically.

Baseline Window
30-minute rolling history
Per-second request counts
Recalculated every 60 seconds
Metrics Used
Mean request rate
Standard deviation

This avoids hardcoded thresholds.

4. Detection Logic

Traffic is flagged when:

z-score > 3
OR
current rate > 5 × baseline mean
z-score Formula
(current_rate - mean) / stddev

This detects sudden spikes and sustained surges.

5. Error Surge Detection

If an IP produces excessive:

4xx responses
5xx responses

at more than 3× baseline error rate, thresholds tighten automatically.

6. Automatic Blocking (iptables)

When a per-IP anomaly is detected:

iptables -A INPUT -s IP_ADDRESS -j DROP

This blocks malicious traffic immediately.

7. Auto-Unban Schedule

Blocked IPs are released using backoff timing:

1st ban  → 10 minutes
2nd ban  → 30 minutes
3rd ban  → 2 hours
4th ban  → Permanent

Slack notifications are sent on every unban.

8. Slack Alerting

Examples:

Global Alert
🌍 GLOBAL ALERT
Rate: 380
Baseline: 12.5
Time: 2026-04-26 18:39 UTC
Ban Alert
🚫 BAN ALERT
IP: x.x.x.x
Condition: Per-IP anomaly
Duration: 10 min
Unban Alert
✅ UNBAN EVENT
IP: x.x.x.x
Released after 10 min
9. Live Dashboard

Dashboard refreshes every 3 seconds and displays:

Uptime
CPU usage
Memory usage
Global request rate
Effective mean/stddev
Top 10 IPs
Active bans
Repository Structure
detector/
  main.py
  monitor.py
  baseline.py
  detector.py
  blocker.py
  unbanner.py
  notifier.py
  dashboard.py
  config.yaml
  requirements.txt

nginx/
  nginx.conf

docs/
  architecture.png

screenshots/

README.md
Setup Instructions (Fresh VPS)
1. Install Dependencies
sudo apt update
sudo apt install docker.io python3 python3-pip python3-venv git apache2-utils -y
2. Clone Repository
git clone https://github.com/Myches/hng-ddos-project.git
cd hng-ddos-project
3.cp .env.example .env
# Edit .env and paste your real Slack webhook URL
cp detector/config.example.yaml detector/config.yaml
docker-compose up -d
4. Start Nextcloud + Nginx
docker-compose up -d
5. Start Detector
cd detector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
Test Traffic
ab -n 20000 -c 200 http://localhost/
Required Screenshots
Tool Running

Slack Ban Alert

Slack Unban Alert

Slack Global Alert

iptables Block Rule

Audit Log

Baseline Dashboard

Blog Post

https://medium.com/@mikeandorful11/how-i-built-a-real-time-ddos-detection-tool-with-python-nginx-docker-and-slack-1fbfca1622a7

GitHub Repository

https://github.com/Myches/hng-ddos-project.git

Final Summary

This project demonstrates:

DevSecOps principles
Real-time monitoring
Statistical anomaly detection
Automated response
Security enforcement
Live observability

It simulates how production systems defend public internet services from malicious traffic.
