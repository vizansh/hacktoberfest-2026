# 🌿 GrassRoots: Local AI Workspace & "Touch Grass" Agent

A lightweight, time-gated desktop assistant built with Python and Google's open-weight **Gemma** model (`gemma:2b` via Ollama) running 100% offline. It balances screen time with real-world health by intelligently shifting between desk ergonomics during work hours and active outdoor micro-breaks.

---

## 💡 Why Open-Source AI Matters Here
* **100% Offline & Private:** Runs entirely on your local machine with zero internet dependency or cloud tracking—keeping your private workspace routines secure.
* **Cost-Free Inference:** Zero API costs, making it sustainable for everyday background execution.
* **Time-Gated Intelligence:** Automatically adapts its behavior based on the time of day:
  * **10:00 AM – 12:00 PM & 5:00 PM – 8:00 PM (Break Windows):** Triggers an audio alert and dynamically generates creative outdoor "Touch Grass" tasks.
  * **12:00 PM – 5:00 PM (Workspace Hours):** Focuses on indoor ergonomics, hydration, and posture check-ins.
  * **Night / Early Morning:** Goes completely dormant during quiet hours.

---

## 🛠️ Tech Stack
* **Language:** Python 3
* **GUI:** Tkinter (Built-in standard library)
* **AI Runtime:** Ollama running locally (`gemma:2b`)
* **Notifications:** Standard library sound alerts (`winsound`)

---

## 🚀 How to Run

1. **Ensure Ollama is running locally with Gemma:**
   ```bash
   ollama run gemma:2b

2. **Run the Application:**
    ```bash 
    python touch_grass.py
    
