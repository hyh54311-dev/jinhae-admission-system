import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_claude_text = "클로드(Claude 3.5 Sonnet 또는 Opus)"
repl_claude_text = "클로드(Claude Sonnet)"

target_claude_desc = "Claude 3.5 Sonnet 또는 Opus"
repl_claude_desc = "Claude Sonnet"

text = text.replace(target_claude_text, repl_claude_text)
text = text.replace(target_claude_desc, repl_claude_desc)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY ACCURATELY UPDATED CLAUDE FREE MODEL ACCORDING TO FACT CHECK!")
