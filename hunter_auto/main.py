import sys
import threading
from datetime import datetime
from scheduler.agent import HunterAgent

# Global objects
agent = None

# Custom Logger to capture prints
class DashboardLogger:
    def __init__(self):
        self.terminal = sys.stdout
        self.logs = []
        
    def write(self, message):
        if message.strip():
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
            self.logs.append(log_entry)
            if len(self.logs) > 100:
                self.logs.pop(0)
        self.terminal.write(message)
        
    def flush(self):
        self.terminal.flush()

sys.stdout = DashboardLogger()

from dashboard.app import app

def start_dashboard():
    app.run(host="0.0.0.0", port=5000, use_reloader=False)

def start_agent():
    global agent
    agent = HunterAgent()
    agent.start()

if __name__ == "__main__":
    print("Starting Hunter Auto PRO OS...")
    print("---------------------------------")
    print("Intelligence: Nous Research Portal + Gemini Active")
    print("Orchestration: Autonomous Scheduler Enabled")
    print("Knowledge: Obsidian Skills Sync Active")
    print("---------------------------------")
    
    # Run Agent in background thread so Flask doesn't block it
    agent_thread = threading.Thread(target=start_agent)
    agent_thread.daemon = True
    agent_thread.start()
    
    # Run Flask Dashboard in main thread
    start_dashboard()

