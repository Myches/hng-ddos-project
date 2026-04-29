from flask import Flask
import psutil
import time
import state

app = Flask(__name__)


@app.route("/")
def home():
    uptime = int(time.time() - state.START_TIME)

    # req/s = requests in last 60s window divided by 60
    global_req_per_s = round(len(state.global_window) / 60, 2)

    top = sorted(
        state.ip_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    rows = "".join(
        f"<tr><td>{ip}</td><td>{count}</td></tr>"
        for ip, count in top
    )

    banned_rows = "".join(
        f"<tr>"
        f"<td>{ip}</td>"
        f"<td>{meta.get('reason', '?')}</td>"
        f"<td>{meta.get('strikes', '?')}</td>"
        f"<td>{'permanent' if meta.get('expires_at') is None else round(meta['expires_at'] - time.time())}s remaining</td>"
        f"</tr>"
        for ip, meta in state.banned_ips.items()
    )

    return f"""
    <html>
    <head>
      <meta http-equiv="refresh" content="3">
      <title>HNG Detector Dashboard</title>
      <style>
        body {{ font-family: monospace; padding: 20px; background: #111; color: #eee; }}
        h1 {{ color: #0f0; }}
        h2 {{ color: #0af; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #444; padding: 6px 12px; text-align: left; }}
        th {{ background: #222; color: #0af; }}
        .stat {{ display: inline-block; margin-right: 30px; }}
        .val {{ font-size: 1.4em; color: #0f0; }}
        .banned td {{ color: #f55; }}
      </style>
    </head>
    <body>
      <h1>🛡️ HNG Anomaly Detection Dashboard</h1>

      <div>
        <div class="stat">Uptime <div class="val">{uptime}s</div></div>
        <div class="stat">CPU <div class="val">{psutil.cpu_percent()}%</div></div>
        <div class="stat">Memory <div class="val">{psutil.virtual_memory().percent}%</div></div>
        <div class="stat">Global req/s <div class="val">{global_req_per_s}</div></div>
        <div class="stat">Mean <div class="val">{state.baseline_mean:.2f}</div></div>
        <div class="stat">Stddev <div class="val">{state.baseline_std:.2f}</div></div>
        <div class="stat">Banned IPs <div class="val">{len(state.banned_ips)}</div></div>
      </div>

      <h2>🚫 Currently Banned IPs</h2>
      <table>
        <tr><th>IP</th><th>Reason</th><th>Strike</th><th>Time Remaining</th></tr>
        <tbody class="banned">{banned_rows or "<tr><td colspan=4>No active bans</td></tr>"}</tbody>
      </table>

      <h2>📊 Top 10 Source IPs</h2>
      <table>
        <tr><th>IP</th><th>Total Requests</th></tr>
        {rows or "<tr><td colspan=2>No data yet</td></tr>"}
      </table>
    </body>
    </html>
    """


def run():
    app.run(host="0.0.0.0", port=5000)
