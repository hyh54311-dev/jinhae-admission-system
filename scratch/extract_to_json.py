import olefile
import os
import re
import json

def get_hwp_text(filename):
    try:
        f = olefile.OleFileIO(filename)
        if ['PrvText'] in f.listdir():
            text = f.openstream('PrvText').read().decode('utf-16le')
            return text
    except:
        pass
    return ""

def extract_plan_info(text, filename):
    info = {}
    match = re.search(r'\(([^)]+)\)\.hwp', filename)
    if not match: match = re.search(r'([가-힣]{2,4})\.hwp', filename)
    info['teacher'] = match.group(1) if match else "미상"
    
    dt_match = re.search(r'일\s*시\s*[:：]?\s*([^\n\r]+)', text)
    loc_match = re.search(r'장\s*소\s*[:：]?\s*([^\n\r]+)', text)
    tgt_match = re.search(r'대\s*상\s*[:：]?\s*([^\n\r]+)', text)
    sub_match = re.search(r'과\s*목\s*[:：]?\s*([^\n\r]+)', text)
    topic_match = re.search(r'(?:주제|단원)\s*[:：]?\s*([^\n\r]+)', text)
    
    info['datetime'] = dt_match.group(1).strip() if dt_match else ""
    info['location'] = loc_match.group(1).strip() if loc_match else ""
    info['target'] = tgt_match.group(1).strip() if tgt_match else ""
    info['subject'] = sub_match.group(1).strip() if sub_match else ""
    info['topic'] = topic_match.group(1).strip() if topic_match else ""
    return info

def extract_feedback_info(text):
    feedback = []
    sections = re.split(r'[\d\.]\s*(?:수업의 장점|제언|참관 소감|의견)', text)
    if len(sections) > 1:
        for s in sections[1:]:
            clean = s.split('\r\n\r\n')[0].strip()
            if clean: feedback.append(clean)
    return " / ".join(feedback)

def main():
    plan_folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과"
    obs_folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록"
    
    plans = []
    for f in os.listdir(plan_folder):
        if f.endswith(".hwp"):
            text = get_hwp_text(os.path.join(plan_folder, f))
            plans.append(extract_plan_info(text, f))
    plans.sort(key=lambda x: x.get('teacher', ''))

    feedbacks = {}
    for f in os.listdir(obs_folder):
        if "참관록" in f and f.endswith(".hwp"):
            text = get_hwp_text(os.path.join(obs_folder, f))
            match = re.search(r'\(([^)]+)\)', f)
            teacher = match.group(1) if match else ""
            if teacher:
                feedbacks[teacher] = extract_feedback_info(text)

    data = {"plans": plans, "feedbacks": feedbacks}
    with open(r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\extracted_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
