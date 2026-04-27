# -*- coding: utf-8 -*-
"""
'국가별 심층분석 > 전체' 서브탭 Step 1 테이블 복구.
지난 refresh 스크립트가 webboard 값으로 잘못 덮어쓴 것을 backup에서 원상 복구.
- 전체(all) 서브탭만 대상
- webboard 탭은 그대로 유지 (최신 값)
"""
import re

CUR = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
BAK = CUR + ".bak.before_refresh"

with open(BAK, 'r', encoding='utf-8') as f: bak = f.read()
with open(CUR, 'r', encoding='utf-8') as f: cur = f.read()

# bak의 전체(all) 서브탭에서 Step 1 tbody 추출
all_panel_re = re.compile(
    r'<div class="ctab-panel active" id="all">(.*?)<div class="ctab-panel" id="kr">',
    re.DOTALL
)
bak_all = all_panel_re.search(bak).group(1)
cur_all_match = all_panel_re.search(cur)
cur_all = cur_all_match.group(1)

tbody_re = re.compile(r'<tbody>\s*\n\s*<tr><td>월평균 매출 \(억원\)</td>.*?</tbody>', re.DOTALL)
bak_tbody = tbody_re.search(bak_all).group()
cur_tbody_m = tbody_re.search(cur_all)

print(f"[bak all tbody] 길이={len(bak_tbody)}")
print(f"[cur all tbody] 길이={len(cur_tbody_m.group())}")

# 전체 서브탭 내 tbody 치환
new_all = cur_all[:cur_tbody_m.start()] + bak_tbody + cur_all[cur_tbody_m.end():]
new_cur = cur[:cur_all_match.start(1)] + new_all + cur[cur_all_match.end(1):]

o = cur.count('<div'); oc = cur.count('</div>')
n = new_cur.count('<div'); nc = new_cur.count('</div>')

with open(CUR, 'w', encoding='utf-8') as f: f.write(new_cur)
print(f"<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")

# 검증
vals_now = re.findall(r'<td class="num[^"]*">([0-9,.]+)</td>',
                     tbody_re.search(all_panel_re.search(new_cur).group(1)).group())
print(f"[복구 후 all Step1 첫 표 값]: {vals_now[:5]}")
