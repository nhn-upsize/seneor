# -*- coding: utf-8 -*-
"""Section 5, 6 끝에 .ng-ins 해석 박스 삽입"""
import re

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
o = html.count('<div'); oc = html.count('</div>')

INS5 = ('  <div class="ng-ins"><strong>핵심:</strong> '
        '25년 후 진입 신작의 12개월 잔존율이 <strong style="color:#059669;">US는 40.8% → 80.0% (+39.2%p) 극적 개선</strong> — '
        '신규 진입 장벽은 올라갔지만 통과한 게임은 장기 생존력 높음. '
        '<strong style="color:#059669;">KR 18.7% → 25.0% (+6.3%p) 소폭 개선</strong>. '
        '반면 <strong style="color:#dc2626;">JP 34.4% → 28.6% (-5.8%p)</strong>로 후 기간 신작의 장기 잔존력 약화. '
        '중장기(M+6 이후) 관점에서 US &gt; KR &gt; JP 순으로 안정.</div>\n')

INS6 = ('  <div class="ng-ins"><strong>핵심:</strong> 퍼블리셔 국적별로 후 기간 잔존율 편차 극단 — '
        '<strong style="color:#059669;">KR 18.9% → 40.0% (+21.1%p)</strong>, '
        '<strong style="color:#059669;">기타 32.7% → 55.6% (+22.9%p)</strong>, '
        '중화권 23.9% → 28.6% (+4.7%p) 개선. '
        'JP/북미는 후 기간 M+12 표본이 작아 (0%로 표시) 해석 주의 — '
        '중화권/KR/기타가 <strong>통계적으로 유의미한 장기 생존 트렌드 보유</strong>.</div>\n')

# Section 5 → Section 6 경계에 INS5 삽입
# 패턴: </div></div>\n</div>\n<div class="ng-section">\n  <div class="ng-section-head">\n    <div class="ng-section-num" ...>6</div>
S5_END_RE = re.compile(
    r'(</div></div>\n)(</div>\n)(<div class="ng-section">\s*\n\s*<div class="ng-section-head">\s*\n\s*<div class="ng-section-num"[^>]*>6</div>)',
    re.DOTALL
)
m = S5_END_RE.search(html)
if not m: raise RuntimeError("Section 5 끝 앵커 못찾음")
html = html[:m.start()] + m.group(1) + INS5 + m.group(2) + m.group(3) + html[m.end():]

# Section 6 → Section 7 경계에 INS6 삽입
S6_END_RE = re.compile(
    r'(</div></div>\n)(</div>\n)(<div class="ng-section">\s*\n\s*<div class="ng-section-head">\s*\n\s*<div class="ng-section-num"[^>]*>7</div>)',
    re.DOTALL
)
m6 = S6_END_RE.search(html)
if not m6: raise RuntimeError("Section 6 끝 앵커 못찾음")
html = html[:m6.start()] + m6.group(1) + INS6 + m6.group(2) + m6.group(3) + html[m6.end():]

with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)
n = html.count('<div'); nc = html.count('</div>')
print(f"<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
