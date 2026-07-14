import json
import sys

# Configure stdout to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\admin\.gemini\antigravity\brain\337abfaa-2ae1-4a62-9818-dab08b9eb7a5\.system_generated\logs\transcript.jsonl"

def main():
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
            except Exception:
                continue
            
            content = data.get("content", "")
            step_idx = data.get("step_index")
            created_at = data.get("created_at")
            
            # Print if it contains any successful runs of KIS, Naver, or Telegram
            if "성공" in content or "access_token" in content or "Response Code: 200" in content:
                # Filter out file view steps to reduce noise
                if data.get("type") in ["VIEW_FILE", "LIST_DIRECTORY"]:
                    continue
                print(f"[{step_idx}] {created_at} ({data.get('type')})")
                print(content[:800])
                print("-" * 80)

if __name__ == "__main__":
    main()
