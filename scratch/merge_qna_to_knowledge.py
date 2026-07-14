# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
knowledge_path = os.path.join(base_dir, 'jinhae-bot', 'jinhae-bot-main', 'api', 'knowledge.txt')
qna_md_path = os.path.join(base_dir, 'scratch', 'qna_final_content.md')

def main():
    print("Reading current knowledge.txt...")
    # Read first 59 lines of knowledge.txt (original knowledge base)
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    # We want to keep only the original section before any Q&A block, in case it was already appended before.
    # To do this safely, we search for "[상세 Q&A 데이터]" block. If it exists, we discard lines from that point onward.
    cleaned_original = []
    for line in original_lines:
        if "[상세 Q&A 데이터]" in line:
            break
        cleaned_original.append(line)
        
    original_text = "".join(cleaned_original).strip()
    
    print("Reading Q&As Markdown content...")
    with open(qna_md_path, 'r', encoding='utf-8') as f:
        qna_content = f.read().strip()
        
    # Combine them
    combined_content = f"""{original_text}

[상세 Q&A 데이터]
{qna_content}
"""

    print("Writing merged content back to knowledge.txt...")
    with open(knowledge_path, 'w', encoding='utf-8') as f:
        f.write(combined_content)
        
    print("SUCCESS: Q&A data merged into knowledge.txt!")

if __name__ == '__main__':
    main()
