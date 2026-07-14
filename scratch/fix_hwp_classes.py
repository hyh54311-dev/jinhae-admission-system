from pyhwpx import Hwp

hwp = Hwp()
hwp.open(r'D:\OneDrive - 경상남도교육청\바탕 화면\안주환장학금 장학증서.hwp')

# Fix classes
hwp.find_replace_all("2학년5반", "2학년 1반")
hwp.find_replace_all("2학년7반", "2학년 2반")
hwp.find_replace_all("3학년1반", "3학년 4반")
hwp.find_replace_all("3학년4반", "3학년 5반")
hwp.find_replace_all("3학년6반", "3학년 7반")

# Fix dates
hwp.find_replace_all("2026년 4월 21일", "2026년 5월 13일")
hwp.find_replace_all("4월 21일", "5월 13일")

hwp.save()
hwp.quit()
print("SUCCESS")
