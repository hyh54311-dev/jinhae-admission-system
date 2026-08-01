import os, sys, re

sys.stdout.reconfigure(encoding='utf-8')

env_files = [
    r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\.env",
    r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\jinhae-bot\jinhae-bot-main\.env",
    r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\jinhae-bot\jinhae-bot-main\api\.env"
]

print("=== Checking .env files for actual API keys ===")
for ep in env_files:
    if os.path.exists(ep):
        print(f"\nFile: {ep}")
        with open(ep, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'GEMINI' in line or 'API_KEY' in line or 'KEY' in line:
                    print("  ", line.strip())
