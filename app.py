from flask import Flask, request, render_template_string
import os
import json

app = Flask(__name__)
LEDGER_FILE = "civicadvocate_abstract_544.ledger"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CivicAdvocate.os // Public Global Registry</title>
    <script src="https://jsdelivr.net"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px 20px; }
        .container { max-width: 900px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 1px solid #334155; }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-top: 0; }
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; align-items: center; }
        .stats-card { background: #0f172a; border: 1px solid #334155; padding: 20px; border-radius: 8px; text-align: center; }
        .stats-val { font-size: 36px; font-weight: bold; color: #38bdf8; margin: 10px 0; }
        .search-box { display: flex; gap: 10px; margin: 20px 0; }
        input[type="text"] { flex: 1; padding: 14px; border: 1px solid #475569; border-radius: 8px; font-size: 16px; background: #0f172a; color: #fff; }
        button { padding: 14px 28px; background: #0284c7; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: 600; transition: background 0.2s; }
        button:hover { background: #0369a1; }
        .block-card { background: #0f172a; border: 1px solid #334155; padding: 20px; border-radius: 8px; margin-top: 15px; }
        .badge { display: inline-block; padding: 4px 10px; background: #0ea5e9; color: #fff; border-radius: 6px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
        .meta { font-size: 11px; color: #94a3b8; font-family: monospace; word-break: break-all; margin-top: 12px; background: #1e293b; padding: 10px; border-radius: 6px; border: 1px solid #334155; }
        .chart-container { max-height: 220px; display: flex; justify-content: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ CivicAdvocate.os Global Public Registry</h1>
        
        <div class="metrics-grid">
            <div class="stats-card">
                <div><strong>Immutably Documented Area</strong></div>
                <div class="stats-val">{{ "%.2f"|format(total_acreage) }} Acres</div>
                <div style="color: #94a3b8; font-size: 13px;">Consensus verified across {{ total_blocks }} chain records</div>
            </div>
            <div class="chart-container">
                <canvas id="statusChart"></canvas>
            </div>
        </div>

        <p style="color: #94a3b8;">Enter an Instrument Number or Volume/Page tracking identifier to run an on-chain forensic audit validation check.</p>
        
        <form class="search-box" method="GET" action="/">
            <input type="text" name="q" placeholder="e.g. 2026-LEASE-99A or V544-P12" value="{{ query }}">
            <button type="submit">Verify Asset</button>
        </form>

        {% if results %}
            <h3>🔍 Cryptographic Evidence Nodes ({{ results|length }} isolated)</h3>
            {% for b in results %}
                <div class="block-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div><strong>Index:</strong> Block Verification Row #{{ b.block_index }}</div>
                        <span class="badge">{{ b.payload.status }}</span>
                    </div>
                    <div style="margin-top: 12px; font-size: 18px; color: #38bdf8;"><strong>Instrument Reference:</strong> {{ b.payload.instrument_number }}</div>
                    <div style="margin-top: 6px;"><strong>Spatial Footprint:</strong> {{ b.payload.acreage }} assigned acres</div>
                    <div><strong>Archival Volume Location:</strong> {{ b.payload.volume_page }}</div>
                    <div style="color: #94a3b8; font-size: 13px; margin-top: 4px;"><strong>Chain Survey Target:</strong> {{ b.survey }}</div>
                    <div class="meta">
                        <strong>Chained Parent Pointer (sha512):</strong> {{ b.previous_hash }}<br>
                        <strong>Secure Block Content Signature (sha512):</strong> {{ b.current_hash }}
                    </div>
                </div>
            {% endfor %}
        {% elif query %}
            <p style="color: #f43f5e; font-weight: bold; background: rgba(244,63,94,0.1); padding: 15px; border-radius: 8px; border: 1px solid #f43f5e;">[EXCEPTION] Target tracking identifier was not resolved within this consensus layer chain database.</p>
        {% endif %}
    </div>

    <script>
        const ctx = document.getElementById('statusChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: {{ chart_labels|tojson }},
                datasets: [{
                    data: {{ chart_values|tojson }},
                    backgroundColor: ['#0284c7', '#10b981', '#f59e0b', '#64748b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'right', labels: { color: '#f8fafc' } } }
            }
        });
    </script>
</body>
</html>
"""

def read_ledger():
    blocks = []
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            for line in f:
                if line.strip():
                    blocks.append(json.loads(line.strip()))
    return blocks

@app.route("/", methods=["GET"])
def home():
    query = request.args.get("q", "").strip()
    all_blocks = read_ledger()
    
    total_acreage = 0.0
    status_counts = {}
    
    for b in all_blocks:
        p = b.get("payload", {})
        if isinstance(p, dict):
            total_acreage += float(p.get("acreage", 0.0))
            status = p.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
            
    results = []
    if query:
        for b in all_blocks:
            p = b.get("payload", {})
            if isinstance(p, dict):
                inst = str(p.get("instrument_number", "")).lower()
                vol = str(p.get("volume_page", "")).lower()
                if query.lower() in inst or query.lower() in vol:
                    results.append(b)

    return render_template_string(
        HTML_TEMPLATE, 
        results=results, 
        query=query,
        total_acreage=total_acreage,
        total_blocks=len(all_blocks),
        chart_labels=list(status_counts.keys()),
        chart_values=list(status_counts.values())
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
