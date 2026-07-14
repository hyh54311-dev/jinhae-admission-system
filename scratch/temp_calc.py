# -*- coding: utf-8 -*-
import os

def calculate_wealth(cagr, seed=100000000, monthly=500000, years=20):
    balance = seed
    monthly_rate = (1 + cagr) ** (1/12) - 1
    
    wealth_history = {}
    for year in range(1, years + 1):
        for month in range(12):
            balance = balance * (1 + monthly_rate) + monthly
        if year in [5, 10, 15, 20]:
            wealth_history[year] = balance
            
    return wealth_history

scenarios = {
    "Dual Momentum (Expected - 12.0%)": 0.12,
    "Dual Momentum (Worst-case - 8.0%)": 0.08,
    "KOSPI Buy & Hold (Expected - 6.6%)": 0.066,
    "KOSPI Buy & Hold (Worst-case - 2.3%)": 0.023
}

seed_val = 100000000
monthly_val = 500000

print("="*80)
print(f"시드: {seed_val:,.0f}원 | 매월 납입: {monthly_val:,.0f}원")
print("="*80)

for name, rate in scenarios.items():
    history = calculate_wealth(rate, seed_val, monthly_val)
    print(f"\n[ {name} ]")
    print(f"  - 총 납입 원금 (20년): {seed_val + monthly_val * 240:,.0f}원")
    print(f"  - 5년차 자산:  {history[5]:,.0f}원 (원금 대비 {history[5]/(seed_val + monthly_val*60)*100:.1f}%)")
    print(f"  - 10년차 자산: {history[10]:,.0f}원 (원금 대비 {history[10]/(seed_val + monthly_val*120)*100:.1f}%)")
    print(f"  - 15년차 자산: {history[15]:,.0f}원 (원금 대비 {history[15]/(seed_val + monthly_val*180)*100:.1f}%)")
    print(f"  - 20년차 자산: {history[20]:,.0f}원 (원금 대비 {history[20]/(seed_val + monthly_val*240)*100:.1f}%)")
print("="*80)
