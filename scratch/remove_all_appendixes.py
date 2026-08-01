import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_app_a = text.find("## 🎁 부록 A")
idx_epilogue = text.find("## 🏁 에필로그")

print(f"idx_app_a: {idx_app_a}, idx_epilogue: {idx_epilogue}")

before_app_a = text[:idx_app_a].rstrip() + "\n\n---\n\n"
after_epilogue = text[idx_epilogue:]

final_text = before_app_a + after_epilogue

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_text)

print("SUCCESSFULLY REMOVED ALL APPENDIX SECTIONS (A & B) FROM MANUSCRIPT!")
