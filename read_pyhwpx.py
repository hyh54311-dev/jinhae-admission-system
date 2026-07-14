import pyhwpx

hwp_path = r'd:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\개인적인 일\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획\2026년 교육대학원연계 AI융합교육 시기.pdf'
original_hwp = r'd:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\개인적인 일\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획.hwp'

hwp = pyhwpx.Hwp()
hwp.open(original_hwp)

# Save as PDF
hwp.SaveAs(hwp_path, "PDF")

# Get text properly
text = hwp.get_text()
# text might be a tuple, so let's check and extract
if isinstance(text, tuple):
    extracted = '\n'.join(str(item) for item in text)
else:
    extracted = str(text)

with open('hwp_extracted_clean.txt', 'w', encoding='utf-8') as f:
    f.write(extracted)

hwp.quit()
