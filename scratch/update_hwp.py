from pyhwpx import Hwp

hwp = Hwp()
hwp.open(r'D:\OneDrive - 경상남도교육청\바탕 화면\안주환장학금 장학증서.hwp')

# 1. Names
hwp.find_replace_all("이창준", "{NAME_1}")
hwp.find_replace_all("박규성", "{NAME_2}")
hwp.find_replace_all("박준영", "{NAME_3}")
hwp.find_replace_all("황상인", "{NAME_4}")
hwp.find_replace_all("성민형", "{NAME_5}")

# 2. Classes (handling possible spaces)
old_classes = [
    ("2학년 5반", "{CLASS_1}"), ("2학년  5반", "{CLASS_1}"),
    ("2학년 7반", "{CLASS_2}"), ("2학년  7반", "{CLASS_2}"),
    ("3학년 1반", "{CLASS_3}"), ("3학년  1반", "{CLASS_3}"),
    ("3학년 4반", "{CLASS_4}"), ("3학년  4반", "{CLASS_4}"),
    ("3학년 6반", "{CLASS_5}"), ("3학년  6반", "{CLASS_5}")
]
for old, new in old_classes:
    hwp.find_replace_all(old, new)

# 3. Insert New Data
hwp.find_replace_all("{NAME_1}", "정은준")
hwp.find_replace_all("{NAME_2}", "이승기")
hwp.find_replace_all("{NAME_3}", "이윤건")
hwp.find_replace_all("{NAME_4}", "조윤성")
hwp.find_replace_all("{NAME_5}", "박예준")

hwp.find_replace_all("{CLASS_1}", "2학년 1반")
hwp.find_replace_all("{CLASS_2}", "2학년 2반")
hwp.find_replace_all("{CLASS_3}", "3학년 4반")
hwp.find_replace_all("{CLASS_4}", "3학년 5반")
hwp.find_replace_all("{CLASS_5}", "3학년 7반")

# 4. Dates and Years
hwp.find_replace_all("2025년 4월 21일", "2026년 5월 13일")
hwp.find_replace_all("2025년  4월 21일", "2026년 5월 13일")
hwp.find_replace_all("2025년 4월  21일", "2026년 5월 13일")
hwp.find_replace_all("2025년  4월  21일", "2026년 5월 13일")

hwp.find_replace_all("4월 21일", "5월 13일")
hwp.find_replace_all("4월  21일", "5월 13일")

hwp.find_replace_all("2025", "2026")

hwp.save()
hwp.quit()
print("SUCCESS")
