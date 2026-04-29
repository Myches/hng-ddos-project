from flask import Flask
import psutil
import time
import state

app = Flask(__name__)

@app.route("/")
def home():
    uptime = int(time.time() - state.START_TIME)

    top = sorted(
        state.ip_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    rows = "".join(
        f"<tr><td>{ip}</td><td>{count}</td></tr>"
        for ip, count in top
    )

    banned = "".join(
        f"<li>{ip} ({meta['reason']})</li>"
        for ip, meta in state.banned_ips.items()
    )

    return f"""
    <html>
    <head>
      <meta http-equiv="refresh" content="3">
      <title>HNG Detector</title>
    </head>
    <body>
      <h1>Live Metrics Dashboard</h1>

      <p>Uptime: {uptime}s</p>
      <p>CPU: {psutil.cpu_percent()}%</p>
      <p>Memory: {psutil.virtual_memory().percent}%</p>

      <p>Global req/60s: {len(state.global_window)}</p>
      <p>Mean: {state.baseline_mean:.2f}</p>
      <p>Stddev: {state.baseline_std:.2f}</p>

      <h2>Banned IPs</h2>
      <ul>{banned}</ul>

      <h2>Top 10 Source IPs</h2>
      <table border=1>
      <tr><th>IP</th><th>Count</th></tr>
      {rows}
      </table>
    </body>
    </html>
    """

def run():
    app.run(host="0.0.0.0", port=5000)
