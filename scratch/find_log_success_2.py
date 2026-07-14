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
            
            # Look for step indices 0 to 900
            if step_idx < 900:
                # We want to find outputs containing 200, KIS, Daum, Naver, Telegram, test_run, etc.
                # but filter out large file contents to avoid truncation.
                if data.get("type") in ["VIEW_FILE", "LIST_DIRECTORY"]:
                    continue
                
                lower_content = content.lower()
                if "telegram" in lower_content or "kis" in lower_content or "naver" in lower_content or "daum" in lower_content or "200" in lower_content:
                    print(f"[{step_idx}] {created_at} ({step_type})")
                    lines = content.split('\n')
                    # print only lines that contain keywords
                    for l in lines:
                        l_lower = l.lower()
                        if "telegram" in l_lower or "kis" in l_lower or "naver" in l_lower or "daum" in l_lower or "success" in l_lower or "성공" in l_lower or "200" in l_lower or "폴백" in l_lower:
                            print(f"  {l[:200]}")
                    print("-" * 80)

if __name__ == "__main__":
    main()
