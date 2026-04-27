# -*- coding: utf-8 -*-
"""
웹보드 탭 Step 1 tbody만 정확히 업데이트 + all sub-tab 복구
- all sub-tab은 backup에서 28,983... 값 복구
- tab-webboard는 새 값 120.4 / 140.9 / 152.4 / 161.7 / 193.7 적용
"""
import re

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
BAK_ALL = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html.bak.before_refresh"

with open(MAIN, 'r', encoding='utf-8') as f: h = f.read()
with open(BAK_ALL, 'r', encoding='utf-8') as f: bak = f.read()

# ============================================================
# 1) all sub-tab Step 1 tbody 복구
# ============================================================
def get_panel(text, pid):
    start = text.find(f'<div class="ctab-panel active" id="{pid}">')
    if start == -1:
        start = text.find(f'<div class="ctab-panel" id="{pid}">')
    if start == -1: return None, None
    cand = [text.find('<div class="ctab-panel', start + 10),
            text.find('<!-- ===== JavaScript', start)]
    cand = [c for c in cand if c > start]
    end = min(cand) if cand else len(text)
    return start, end

tbody_re = re.compile(r'<tbody>\s*\n?\s*<tr><td>월평균 매출 \(억원\)</td>.*?</tbody>', re.DOTALL)

# bak에서 all 패널의 Step1 tbody
bak_s, bak_e = get_panel(bak, 'all')
bak_all = bak[bak_s:bak_e]
bak_tbody_m = tbody_re.search(bak_all)
if not bak_tbody_m:
    raise RuntimeError("bak all tbody 못찾음")
good_all_tbody = bak_tbody_m.group()

# 현재 all 패널
h_s, h_e = get_panel(h, 'all')
h_all = h[h_s:h_e]
h_tbody_m = tbody_re.search(h_all)
if not h_tbody_m:
    raise RuntimeError("현재 all tbody 못찾음")

new_h_all = h_all[:h_tbody_m.start()] + good_all_tbody + h_all[h_tbody_m.end():]
h = h[:h_s] + new_h_all + h[h_e:]

# ============================================================
# 2) tab-webboard Step 1 tbody 새 값으로 교체
# ============================================================
new_wb_tbody = """<tbody>
        <tr><td>월평균 매출 (억원)</td>
          <td class="num">120.4</td>
          <td class="num up">140.9</td>
          <td class="num up">152.4</td>
          <td class="num up">161.7</td>
          <td class="num col26 up">193.7</td>
          <td class="num up"><strong>138 → 168</strong><br>+30억 (+22%)</td>
        </tr>
        <tr><td>월평균 MAU (만명)</td>
          <td class="num">182</td>
          <td class="num dn">126</td>
          <td class="num dn">93</td>
          <td class="num dn">99</td>
          <td class="num col26 up">131</td>
          <td class="num dn"><strong>134 → 105</strong><br>-28만 (-21%)</td>
        </tr>
        <tr><td>ARPMAU (원/MAU)</td>
          <td class="num">6,601</td>
          <td class="num up">11,148</td>
          <td class="num up">16,390</td>
          <td class="num up">16,391</td>
          <td class="num col26 dn">14,764</td>
          <td class="num up"><strong>11,380 → 16,066</strong><br>+4,686원 (+41%)</td>
        </tr>
      </tbody>"""

# webboard 탭 범위
wb_s = h.find('<div id="tab-webboard"')
wb_e = h.find('<!-- ===== JavaScript', wb_s)
if wb_e == -1: wb_e = h.find('<script>', wb_s)
wb = h[wb_s:wb_e]
wb_tbody_m = tbody_re.search(wb)
if not wb_tbody_m:
    raise RuntimeError("webboard tbody 못찾음")
new_wb = wb[:wb_tbody_m.start()] + new_wb_tbody + wb[wb_tbody_m.end():]
h = h[:wb_s] + new_wb + h[wb_e:]

# ============================================================
# 3) webboard 탭 헤드라인도 업데이트 (146→169 (+16%) → 138→168 (+22%))
# ============================================================
wb_s = h.find('<div id="tab-webboard"')
wb_e = h.find('<!-- ===== JavaScript', wb_s)
wb = h[wb_s:wb_e]
# 141 → 169 이거나 146 → 169 같은 패턴 교체
wb = re.sub(
    r'월평균 매출 14[016]억원 \(22~24\) → 169억원 \(25~26\.1Q\) \(\+[0-9]+%\)',
    '월평균 매출 138억원 (22~24) → 168억원 (25~26.1Q) (+22%)',
    wb
)
h = h[:wb_s] + wb + h[wb_e:]

# 저장 + 검증
with open(MAIN, 'w', encoding='utf-8') as f: f.write(h)
n_open = h.count('<div'); n_close = h.count('</div>')
print(f"<div>={n_open}, </div>={n_close}  {'✅' if n_open==n_close else '❌'}")

# 확인
tbs = list(tbody_re.finditer(h))
for i, m in enumerate(tbs):
    nums = re.findall(r'>([0-9.,]+)</', m.group()[:400])
    print(f'[매출 tbody #{i+1}] 앞 5개: {nums[:5]}')
