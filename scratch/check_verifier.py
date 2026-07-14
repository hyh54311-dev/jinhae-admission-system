import json
import os

path = r"C:\Users\요한T\.gemini\antigravity\brain\d0c8631c-e89d-4733-8ec8-8daae460e6e9\.system_generated\logs\transcript.jsonl"
if os.path.exists(path):
    with open(path, encoding='utf-8') as f:
        lines = [json.loads(line) for line in f]
    print("Total steps:", len(lines))
    
    # Check if the subagent has finished and printed their final message
    # Usually the final step of the subagent has source == "MODEL" and is the last PLANNER_RESPONSE
    responses = [l for l in lines if l.get("type") == "PLANNER_RESPONSE" and l.get("source") == "MODEL"]
    if responses:
        last_response = responses[-1]
        content = last_response.get("content", "")
        print("LAST_RESPONSE_FOUND")
        print(content)
    else:
        print("NO_RESPONSES_FOUND")
else:
    print("Path does not exist")
