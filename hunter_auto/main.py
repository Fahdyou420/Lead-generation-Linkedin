from scheduler.agent import HunterAgent
from dashboard.app import app
import threading

def start_dashboard():
    app.run(host="0.0.0.0", port=5000, use_reloader=False)

def start_agent():
    agent = HunterAgent()
    agent.start()

if __name__ == "__main__":
    print("Starting Hunter Auto 1.0...")
    
    # Run Agent in background thread so Flask doesn't block it
    agent_thread = threading.Thread(target=start_agent)
    agent_thread.daemon = True
    agent_thread.start()
    
    # Run Flask Dashboard in main thread
    start_dashboard()
