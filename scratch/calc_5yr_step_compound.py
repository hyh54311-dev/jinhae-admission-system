import sys
sys.stdout.reconfigure(encoding='utf-8')

annual_deposit = 6000000
rate = 0.10
tax_rate = 0.154
effective_rate = rate * (1 - tax_rate)

print("=== 5-YEAR PERIOD COMPOUND INTEREST & TAX DEFERRAL AUDIT ===")
print(f"{'기간':<6} | {'누적 투입 원금':<12} | {'일반 계좌 (15.4% 과세)':<18} | {'일반 누적 이자':<12} | {'연금저축 (과세이연)':<18} | {'연금 누적 이자':<12} | {'과세이연 이자 격차':<12}")
print("-" * 105)

for yr in [5, 10, 15, 20]:
    # 연금저축
    fv_pension = 0
    for t in range(yr):
        fv_pension = (fv_pension + annual_deposit) * (1 + rate)
    
    # 일반계좌
    fv_general = 0
    for t in range(yr):
        fv_general = (fv_general + annual_deposit) * (1 + effective_rate)
    
    principal = annual_deposit * yr
    pension_interest = fv_pension - principal
    general_interest = fv_general - principal
    diff_interest = fv_pension - fv_general
    
    print(f"{yr:<4}년 차 | {principal/10000:>8.0f}만 원 | {fv_general/10000:>14.0f}만 원 | {general_interest/10000:>8.0f}만 원 | {fv_pension/10000:>14.0f}만 원 | {pension_interest/10000:>8.0f}만 원 | +{diff_interest/10000:>8.0f}만 원")
