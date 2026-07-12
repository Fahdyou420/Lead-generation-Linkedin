from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database.sheets_client import SheetsClient
from config.settings import TARGET_SECTORS
import os
import sys

app = Flask(__name__)
CORS(app) # Enable cross-origin requests from the Google AI Studio dashboard
db = SheetsClient()

@app.route("/")
def index():
    stats = db.get_stats()
    # Get last 10 leads
    records = db.get_all_leads_records()
    recent = list(reversed(records))[:10]
    return render_template("index.html", stats=stats, recent=recent)

@app.route("/leads")
def leads():
    all_leads = db.get_all_leads_records()
    return render_template("leads.html", leads=reversed(all_leads))

@app.route("/leads/<int:lead_id>/approve", methods=["POST"])
def approve_lead(lead_id):
    db.update_lead_status(lead_id, "meeting_booked")
    return "<span class='badge bg-success'>Meeting Booked</span>"

@app.route("/leads/<int:lead_id>/skip", methods=["POST"])
def skip_lead(lead_id):
    db.update_lead_status(lead_id, "not_interested")
    return "<span class='badge bg-secondary'>Skipped</span>"

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        sectors = request.form.getlist("sectors")
        # In a real app we'd update .env, but here we just update memory for demo
        global TARGET_SECTORS
        print("Sectors updated to:", sectors)
        return render_template("settings.html", sectors=sectors, saved=True)
        
    return render_template("settings.html", sectors=TARGET_SECTORS, saved=False)

@app.route("/api/stats")
def api_stats():
    stats = db.get_stats()
    # Snippet for HTMX to swap
    return f"""
    <div class="stat-value">{stats['total']}</div>
    <div>Total Leads</div>
    """
    
@app.route("/api/dashboard")
def api_dashboard():
    stats = db.get_stats()
    sheet = db.get_leads_sheet()
    recent = []
    if sheet:
        records = sheet.get_all_records()
        recent = list(reversed(records))[:10]
        
    logs = getattr(sys.stdout, "logs", ["Logging not initialized"])
    
    # Try to determine state
    state = "running"
    # To check if scheduler is paused:
    import main
    if main.agent and main.agent.scheduler.state == 0: # 0 means stopped
        state = "stopped"
    elif main.agent and main.agent.scheduler.state == 2: # 2 means paused
        state = "paused"
        
    return jsonify({
        "status": "online",
        "version": "2.0",
        "agent_state": state,
        "logs": list(reversed(logs))[:50], # latest 50
        "stats": stats,
        "recent": recent,
        "active_sectors": TARGET_SECTORS
    })

@app.route("/api/agent/pause", methods=["POST"])
def agent_pause():
    import main
    if main.agent:
        main.agent.scheduler.pause()
        print("Agent PAUSED")
    return jsonify({"status": "paused"})

@app.route("/api/agent/resume", methods=["POST"])
def agent_resume():
    import main
    if main.agent:
        main.agent.scheduler.resume()
        print("Agent RESUMED")
    return jsonify({"status": "running"})

@app.route("/api/agent/scrape_now", methods=["POST"])
def agent_scrape_now():
    import main
    if main.agent:
        print("Manual Scrape TRIGGERED")
        # Run in thread so it doesn't block API
        import threading
        threading.Thread(target=main.agent.scrape_job).start()
    return jsonify({"status": "scraping_started"})


# Start Flask only if run directly (though main.py handles it)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
