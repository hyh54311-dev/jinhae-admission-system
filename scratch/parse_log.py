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
            step_type = data.get("type")
            
            # Print if it contains mentions of KIS response or successful execution logs
            if "Response Code: 200" in content or "성공" in content or "10:30" in content or "수급 데이터 수집" in content:
                print(f"[{step_idx}] {created_at} ({step_type})")
                print(f"--- CONTENT PREVIEW ---")
                print(content[:600])
                print("-" * 50)

if __name__ == "__main__":
    main()
