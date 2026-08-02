import sys
sys.stdout.reconfigure(encoding='utf-8')

annual_deposit = 6000000
years = 20
rate = 0.10
tax_rate = 0.154

fv_pension = 0
for t in range(years):
    fv_pension = (fv_pension + annual_deposit) * (1 + rate)

effective_rate = rate * (1 - tax_rate)
fv_general = 0
for t in range(years):
    fv_general = (fv_general + annual_deposit) * (1 + effective_rate)

after_tax_lump = fv_pension * (1 - 0.165)
after_tax_annuity = fv_pension * (1 - 0.055)

print(f"총 원금 (20년 간 연 600만 원): {annual_deposit * years / 10000:.0f}만 원 (1.2억 원)")
print(f"1. 연금저축펀드 계좌 (과세이연 100% 세전 자산): {fv_pension / 10000:.0f}만 원 (약 3억 7,800만 원)")
print(f"2. 일반 주식 계좌 (매년 15.4% 세금 차감 세후 자산): {fv_general / 10000:.0f}만 원 (약 3억 1,340만 원)")
print(f"   ➔ 과세이연 효과로 불어난 세전 자본 차이: 무려 {(fv_pension - fv_general) / 10000:.0f}만 원 (약 6,460만 원 더 커짐!)")
print(f"3. 연금저축 최악 일시금 해지 시 (16.5% 세금 후 실수령): {after_tax_lump / 10000:.0f}만 원 (약 3억 1,560만 원)")
print(f"4. 연금저축 정상 연금 수령 시 (5.5% 세금 후 실수령): {after_tax_annuity / 10000:.0f}만 원 (약 3억 5,720만 원)")
