import datetime
import json
import urllib.request
import time
import winsound  # Built-in Windows notification sound
import tkinter as tk

# Local Ollama endpoint (runs 100% offline via open-weight Gemma)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma:2b"

def query_local_ai(prompt_type):
    if prompt_type == "outdoor":
        prompt = "Give one creative, brief outdoor 'touch grass' micro-task (under 15 words) to get someone away from their screen."
    else:
        prompt = "Give one brief office ergonomics or hydration health tip (under 15 words) for a developer at a desk."
        
    data = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }).encode('utf-8')
    
    req = urllib.request.Request(
        OLLAMA_URL, 
        data=data, 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "").strip()
    except Exception as e:
        return "Fallback: Take a 5-minute screen break, stretch, and step away!"

class GrassRootsAgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GrassRoots - Local AI Assistant")
        self.root.geometry("420x260")
        self.root.config(bg="#f4f8f3")
        
        # Header
        self.title_lbl = tk.Label(root, text="🌿 GrassRoots AI (Local Gemma)", font=("Arial", 13, "bold"), bg="#f4f8f3", fg="#2e5d30")
        self.title_lbl.pack(pady=10)
        
        # Status
        self.status_lbl = tk.Label(root, text="Status: Agent standing by...", font=("Arial", 9, "italic"), bg="#f4f8f3", fg="#666")
        self.status_lbl.pack(pady=2)
        
        # Task Box
        self.task_box = tk.Label(root, text="Click below to trigger an AI check-in.", font=("Arial", 10), bg="white", fg="#333", wraplength=370, relief="solid", bd=1, padx=10, pady=10)
        self.task_box.pack(pady=10, fill="x", padx=20)
        
        # Button
        self.btn = tk.Button(root, text="Run AI Check-In Now", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=self.run_check_in)
        self.btn.pack(pady=5)

    def run_check_in(self):
        now = datetime.datetime.now()
        hour = now.hour
        
        # Time-Gated Logic & Intervals
        if (10 <= hour < 12) or (17 <= hour < 20):
            p_type = "outdoor"
            mode_desc = "🌿 Break Window (Every 30m Outdoor Prompt)"
            # Play alert sound for break window
            winsound.Beep(1000, 300) 
        elif 12 <= hour < 17:
            p_type = "indoor"
            mode_desc = "💻 Workspace Hours (Every 60m Ergonomics Prompt)"
            winsound.Beep(800, 200)
        else:
            self.status_lbl.config(text="Status: Quiet Hours 🌙")
            self.task_box.config(text="Agent is dormant outside scheduled active hours.")
            return

        self.status_lbl.config(text=f"Active Mode: {mode_desc}")
        self.root.update_idletasks()
        
        # Fetch dynamic prompt from local open-weight Gemma
        ai_task = query_local_ai(p_type)
        self.task_box.config(text=ai_task)

if __name__ == "__main__":
    root = tk.Tk()
    app = GrassRootsAgentApp(root)
    root.mainloop()