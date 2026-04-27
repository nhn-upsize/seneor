# -*- coding: utf-8 -*-
"""전체(all) 탭 Step 1 tbody + 스파크라인 + 해석을 unified 기준으로 통일"""
import os, re

path = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# Unified 3국 합산 실측값 (방금 쿼리 결과)
REV = {'2022':28222,'2023':29419,'2024':33004,'2025':33857,'26.1Q':31368}
MAU = {'2022':45029,'2023':43072,'2024':41694,'2025':42033,'26.1Q':42435}
ARP = {'2022':6268,'2023':6830,'2024':7916,'2025':8055,'26.1Q':7392}
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

def ba(d):
    b = sum(d[y]*YR_M[y] for y in ['2022','2023','2024'])/36
    a = sum(d[y]*YR_M[y] for y in ['2025','26.1Q'])/15
    return b, a

rev_b, rev_a = ba(REV); rev_pct = (rev_a-rev_b)/rev_b*100
mau_b, mau_a = ba(MAU); mau_pct = (mau_a-mau_b)/mau_b*100
arp_b, arp_a = ba(ARP); arp_pct = (arp_a-arp_b)/arp_b*100

print(f"전후 매출: {rev_b:,.0f} → {rev_a:,.0f} (+{rev_a-rev_b:,.0f}억, +{rev_pct:.0f}%)")
print(f"전후 MAU: {mau_b:,.0f} → {mau_a:,.0f} ({mau_a-mau_b:+,.0f}만, {mau_pct:+.1f}%)")
print(f"전후 ARPMAU: {arp_b:,.0f} → {arp_a:,.0f} (+{arp_a-arp_b:,.0f}원, +{arp_pct:.1f}%)")

# 새 tbody
new_tbody = f"""<tbody>
        <tr><td>월평균 매출 (억원)</td>
          <td class="num">{REV['2022']:,}</td>
          <td class="num up">{REV['2023']:,}</td>
          <td class="num up">{REV['2024']:,}</td>
          <td class="num up">{REV['2025']:,}</td>
          <td class="num col26 dn">{REV['26.1Q']:,}</td>
          <td class="num up"><strong>{rev_b:,.0f} → {rev_a:,.0f}</strong><br>+{rev_a-rev_b:,.0f}억 (+{rev_pct:.0f}%)</td>
        </tr>
        <tr><td>월평균 MAU (만명)</td>
          <td class="num">{MAU['2022']:,}</td>
          <td class="num dn">{MAU['2023']:,}</td>
          <td class="num dn">{MAU['2024']:,}</td>
          <td class="num up">{MAU['2025']:,}</td>
          <td class="num col26 up">{MAU['26.1Q']:,}</td>
          <td class="num dn"><strong>{mau_b:,.0f} → {mau_a:,.0f}</strong><br>{mau_a-mau_b:+,.0f}만 ({mau_pct:+.1f}%)</td>
        </tr>
        <tr><td>ARPMAU (원/MAU)</td>
          <td class="num">{ARP['2022']:,}</td>
          <td class="num up">{ARP['2023']:,}</td>
          <td class="num up">{ARP['2024']:,}</td>
          <td class="num up">{ARP['2025']:,}</td>
          <td class="num col26 dn">{ARP['26.1Q']:,}</td>
          <td class="num up"><strong>{arp_b:,.0f} → {arp_a:,.0f}</strong><br>+{arp_a-arp_b:,.0f}원 (+{arp_pct:.1f}%)</td>
        </tr>
      </tbody>"""

# 헤드라인 교체 (all 탭)
new_headline = f'<h2>🌏 전체 시장 (KR+JP+US 합산): 월평균 매출 {rev_b:,.0f}억 → {rev_a:,.0f}억 (+{rev_pct:.0f}%)</h2>'

with open(path, 'r', encoding='utf-8') as f: h = f.read()
o = h.count('<div'); oc = h.count('</div>')

# 전체 sub-tab 범위 (id="all")
all_start = h.find('<div class="ctab-panel active" id="all">')
all_end = h.find('<div class="ctab-panel" id="kr">', all_start)
all_sec = h[all_start:all_end]

# Step 1 tbody 교체
tbody_re = re.compile(r'<tbody>\s*\n?\s*<tr><td>월평균 매출 \(억원\)</td>.*?</tbody>', re.DOTALL)
m = tbody_re.search(all_sec)
if m:
    all_sec = all_sec[:m.start()] + new_tbody + all_sec[m.end():]
    print("[tbody] 교체 ✓")

# 헤드라인 교체
all_sec = re.sub(
    r'<h2>🌏 전체 시장 \(KR\+JP\+US 합산\): 월평균 매출 [^<]+</h2>',
    new_headline, all_sec, count=1
)

# sub 문구에서 +3,148억 값도 수정 (3,144로)
diff = int(round(rev_a - rev_b))
all_sec = all_sec.replace('+3,148억 성장', f'+{diff:,}억 성장')
all_sec = all_sec.replace('월평균 +3,148억 성장', f'월평균 +{diff:,}억 성장')

h = h[:all_start] + all_sec + h[all_end:]

n = h.count('<div'); nc = h.count('</div>')
with open(path, 'w', encoding='utf-8') as f: f.write(h)
print(f"<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
