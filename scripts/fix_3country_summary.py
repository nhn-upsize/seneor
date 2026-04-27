# -*- coding: utf-8 -*-
"""3국 시장 한눈에 섹션의 모든 수치를 unified 기준으로 통일"""
import os, re

path = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
with open(path, 'r', encoding='utf-8') as f:
    h = f.read()
o_open = h.count('<div'); o_close = h.count('</div>')

# KR 연도별 값 (억원)
replacements = [
    # KR 숫자
    ('>3,894<', '>3,835<'),
    ('>4,080<', '>4,003<'),
    ('>4,570<', '>4,488<'),
    ('>4,886<', '>4,800<'),
    ('>4,159<', '>4,071<'),
    # KR YoY %
    ('>+4.8%<', '>+4.4%<'),
    ('>+12.0%<', '>+12.1%<'),
    ('>+6.9%<', '>+7.0%<'),
    ('>-14.9%<', '>-15.2%<'),
    # JP 숫자
    ('>9,909<', '>9,700<'),
    ('>9,297<', '>9,062<'),
    ('>9,375<', '>9,157<'),
    ('>9,273<', '>9,058<'),
    ('>8,815<', '>8,611<'),
    # JP YoY %
    ('>-6.2%<', '>-6.6%<'),
    ('>+0.8%<', '>+1.0%<'),
    # US 조 표기
    ('>1.52조<', '>1.47조<'),
    ('>1.68조<', '>1.64조<'),
    ('>1.98조<', '>1.94조<'),
    ('>2.05조<', '>2.00조<'),
    ('>1.92조<', '>1.87조<'),
    # US YoY %
    ('>+10.8%<', '>+11.4%<'),
    ('>+17.9%<', '>+18.4%<'),
    ('>+3.2%<', '>+3.3%<'),
    ('>-6.1%<', '>-6.6%<'),
    # 전후 요약
    ('4,181억 → 4,740억 (+559억, +13%)', '4,109억 → 4,654억 (+545억, +13%)'),
    ('9,527억 → 9,181억 (-346억, -4%)', '9,306억 → 8,969억 (-337억, -4%)'),
    ('1.73조 → 2.02조 (+2,935억, +17%)', '1.68조 → 1.97조 (+2,935억, +17%)'),
]

applied = 0
for old, new in replacements:
    if old in h:
        h = h.replace(old, new, 1)
        applied += 1

print(f"[적용] {applied}/{len(replacements)}개 교체")

# 변경 안 된 항목 알림
for old, new in replacements:
    if old in h:  # 아직 남아있으면 old 중복 있었다는 뜻
        print(f"  (남음) {old} → {new}")

n_open = h.count('<div'); n_close = h.count('</div>')
with open(path, 'w', encoding='utf-8') as f: f.write(h)
print(f"<div> {o_open}→{n_open}, </div> {o_close}→{n_close}  {'✅' if n_open==n_close else '❌'}")
