from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database.sheets_client import SheetsClient
from config.settings import (
    load_config, save_config, load_status, update_status,
    get_target_sectors, get_target_cities, get_target_titles,
    get_scrape_interval, get_outreach_limit
)
import os
import sys
import json

app = Flask(__name__)
CORS(app) # Enable cross-origin requests from the Google AI Studio dashboard
db = SheetsClient()

@app.route("/")
def index():
    stats = db.get_stats()
    records = db.get_all_leads_records()
    recent = list(reversed(records))[:10]
    status_info = load_status()
    return render_template("index.html", stats=stats, recent=recent, status=status_info)

@app.route("/leads")
def leads():
    all_leads = db.get_all_leads_records()
    return render_template("leads.html", leads=reversed(all_leads))

@app.route("/leads/<lead_id>/approve", methods=["POST"])
def approve_lead(lead_id):
    db.update_lead_status(lead_id, "meeting_booked")
    return "<span class='badge bg-success'>Meeting Booked</span>"

@app.route("/leads/<lead_id>/skip", methods=["POST"])
def skip_lead(lead_id):
    db.update_lead_status(lead_id, "not_interested")
    return "<span class='badge bg-secondary'>Skipped</span>"

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Support both checklist sectors and custom sectors/cities/titles comma-separated inputs
        sectors_list = request.form.getlist("sectors")
        if not sectors_list and request.form.get("custom_sectors"):
            sectors_list = [s.strip() for s in request.form.get("custom_sectors").split(",") if s.strip()]
            
        cities = [c.strip() for c in request.form.get("cities", "").split(",") if c.strip()]
        titles = [t.strip() for t in request.form.get("titles", "").split(",") if t.strip()]
        
        try:
            scrape_interval = int(request.form.get("scrape_interval", 2))
            outreach_limit = int(request.form.get("outreach_limit", 15))
        except:
            scrape_interval = 2
            outreach_limit = 15

        cfg = load_config()
        if sectors_list:
            cfg["TARGET_SECTORS"] = sectors_list
        if cities:
            cfg["TARGET_CITIES"] = cities
        if titles:
            cfg["TARGET_TITLES"] = titles
            
        cfg["SCRAPE_INTERVAL_HOURS"] = scrape_interval
        cfg["OUTREACH_DAILY_LIMIT"] = outreach_limit
        
        save_config(cfg)
        
        return render_template(
            "settings.html",
            sectors=get_target_sectors(),
            cities=",".join(get_target_cities()),
            titles=",".join(get_target_titles()),
            scrape_interval=get_scrape_interval(),
            outreach_limit=get_outreach_limit(),
            saved=True
        )
        
    return render_template(
        "settings.html",
        sectors=get_target_sectors(),
        cities=",".join(get_target_cities()),
        titles=",".join(get_target_titles()),
        scrape_interval=get_scrape_interval(),
        outreach_limit=get_outreach_limit(),
        saved=False
    )

@app.route("/api/stats")
def api_stats():
    stats = db.get_stats()
    return f"""
    <div class="stat-value">{stats['total']}</div>
    <div>Total Leads</div>
    """
    
@app.route("/api/dashboard")
def api_dashboard():
    stats = db.get_stats()
    recent = db.get_all_leads_records()
    recent_ten = list(reversed(recent))[:10]
        
    logs = getattr(sys.stdout, "logs", ["Logging not initialized"])
    
    # Try to determine state
    state = "running"
    try:
        import main
        if main.agent and main.agent.scheduler.state == 0: # 0 means stopped
            state = "stopped"
        elif main.agent and main.agent.scheduler.state == 2: # 2 means paused
            state = "paused"
    except Exception as e:
        print(f"Error checking scheduler state: {e}")
        
    # Inject latest real-time status tracker values
    status_info = load_status()
    
    return jsonify({
        "status": "online",
        "version": "2.0",
        "agent_state": state,
        "logs": list(reversed(logs))[:50], # latest 50
        "stats": stats,
        "recent": recent_ten,
        "active_sectors": get_target_sectors(),
        "active_cities": get_target_cities(),
        "active_titles": get_target_titles(),
        "scrape_interval": get_scrape_interval(),
        "outreach_limit": get_outreach_limit(),
        "status_info": status_info
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
        import threading
        threading.Thread(target=main.agent.scrape_job).start()
    return jsonify({"status": "scraping_started"})

@app.route("/api/chat", methods=["GET", "POST"])
def api_chat():
    memory_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "chat_memory.json")
    
    if request.method == "POST":
        req_data = request.json or {}
        user_message = req_data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
            
        history = []
        if os.path.exists(memory_file):
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                pass
                
        prompt = "You are Hunter, the autonomous Tunisian lead-generation and sales agent. You help the user manage the system, brainstorm strategies, and customize their targeting.\n\n"
        prompt += "Here is the conversation history:\n"
        for msg in history[-10:]: # Context limit
            prompt += f"{msg['role'].upper()}: {msg['content']}\n"
        prompt += f"USER: {user_message}\n"
        prompt += "HUNTER:"
        
        from ai.ai_client import AIClient
        ai = AIClient()
        try:
            reply = ai.generate(prompt)
        except Exception as e:
            reply = f"Error generating response from AI model: {e}"
            
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        
        try:
            os.makedirs(os.path.dirname(memory_file), exist_ok=True)
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chat history: {e}")
            
        return jsonify({"reply": reply, "history": history})
        
    history = []
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass
    return jsonify({"history": history})

# Start Flask only if run directly (though main.py handles it)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
