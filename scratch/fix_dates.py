from pyhwpx import Hwp

hwp = Hwp()
hwp.open(r'D:\OneDrive - 경상남도교육청\바탕 화면\안주환장학금 장학증서.hwp')

# Try replacing parts
hwp.find_replace_all("2026년 4월 21일", "2026년 5월 13일")
hwp.find_replace_all("4월 21일", "5월 13일")
hwp.find_replace_all("4월", "5월")
hwp.find_replace_all("21일", "13일")

# Just in case it's still 2025
hwp.find_replace_all("2025년 4월 21일", "2026년 5월 13일")

hwp.save()
hwp.quit()
print("SUCCESS")
