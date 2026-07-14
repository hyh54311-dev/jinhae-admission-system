import os
import subprocess
import sys
import webbrowser
import time
import io

# Force UTF-8 encoding for Windows console output if possible
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def run():
    print("--------------------------------------------------")
    print("Jinhae High School Chatbot 2.0 Launcher")
    print("--------------------------------------------------")
    
    # 1. Install dependencies
    print("[1/2] Checking and installing dependencies (fastapi, uvicorn, requests)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "requests", "--quiet"])
        print("[OK] Dependencies ready.")
    except Exception as e:
        print(f"[Error] Failed to install dependencies: {e}")
        return

    # 2. Start the server and open browser
    print("\n[2/2] Starting server at http://localhost:8000 ...")
    print("??If the browser doesn't open, visit http://localhost:8000 manually.")
    print("--------------------------------------------------")
    
    # Open browser slightly after server starts
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Start the server
    try:
        # Run start_chat.py
        subprocess.run([sys.executable, "start_chat.py"])
    except KeyboardInterrupt:
        print("\n\n?몝 Stopping chatbot server...")
    except Exception as e:
        print(f"[Error] Server error: {e}")

if __name__ == "__main__":
    run()
