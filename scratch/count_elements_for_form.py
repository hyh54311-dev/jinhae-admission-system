import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

tables_count = text.count("| :---")
code_blocks_count = text.count("```python")
mermaid_count = text.count("```mermaid")
tip_boxes_count = text.count("> 💡") + text.count("> 💰") + text.count("> 🛡️")
footnotes_count = text.count("* (※") + text.count("*(※")

print(f"Tables: {tables_count}")
print(f"Code Blocks (Python): {code_blocks_count}")
print(f"Mermaid Diagrams: {mermaid_count}")
print(f"Tip Boxes: {tip_boxes_count}")
print(f"Footnotes/Notes: {footnotes_count}")
