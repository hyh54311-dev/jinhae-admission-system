import sys

# 월 50만 원 (연 600만 원) 20년 적립 (총 240개월 / 총 원금 1.2억 원)
# 연 10% 수익률 (월 복리 0.8333% 또는 연복리 계산)
# 연복리 기준 계산 (매년 말 600만 원 납입)

annual_deposit = 6000000
years = 20
rate = 0.10  # 연 10%
tax_rate = 0.154  # 일반계좌 세금

# 1. 연금저축계좌 (세금 0원 과세이연)
fv_pension = 0
for t in range(years):
    fv_pension = (fv_pension + annual_deposit) * (1 + rate)

# 2. 일반계좌 (매년 수익에 대해 15.4% 세금 차감)
# 실질 연 수익률 = 10% * (1 - 0.154) = 8.46%
effective_rate = rate * (1 - tax_rate)
fv_general = 0
for t in range(years):
    fv_general = (fv_general + annual_deposit) * (1 + effective_rate)

# 연금저축 인출 시나리오
# A. 최악의 일시금 해지 (원금 1.2억 제외한 연금저축 이익금 및 세액공제분에 대해 16.5% 기타소득세)
# 세액공제 받고 넣은 1.2억 + 이익금 전체에 대해 16.5% 징수
after_tax_lump = fv_pension * (1 - 0.165)

# B. 정상 연금 수령 (5.5% 연금소득세 적용 시)
after_tax_annuity = fv_pension * (1 - 0.055)

print(f"총 원금 (20년 간 연 600만 원): {annual_deposit * years / 10000:.0f}만 원")
print(f"1. 연금저축계좌 (과세이연 100%): {fv_pension / 10000:.0f}만 원")
print(f"2. 일반주식계좌 (매년 15.4% 과세): {fv_general / 10000:.0f}만 원")
print(f"3. 연금저축 최악 일시금 해지 시 (16.5% 세금 후 실수령): {after_tax_lump / 10000:.0f}만 원")
print(f"4. 연금저축 정상 연금 수령 시 (5.5% 세금 후 실수령): {after_tax_annuity / 10000:.0f}만 원")
