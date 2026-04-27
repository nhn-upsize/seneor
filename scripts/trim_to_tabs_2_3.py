# -*- coding: utf-8 -*-
"""
메인 HTML에서 탭 2(25년 성장 게임), 탭 3(신규 진입 게임) 만 남긴 버전 생성.
- 탭 바 재구성 (버튼 2개만)
- 다른 탭 panel div 전체 제거 (tab-country-deep, tab-insight, tab-criteria, tab-webboard)
- 탭 2를 active로 설정
- div 밸런스 검증
"""
import re

SRC = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
DST = r"C:\Users\NHN\Documents\sensortower_api\reports\_share\NHN_growth_newgame_only.html"

with open(SRC, 'r', encoding='utf-8') as f:
    h = f.read()
o_open = h.count('<div'); o_close = h.count('</div>')
print(f"[원본] <div>={o_open}, </div>={o_close}")

# ============================================================
# 1) 탭 바 재구성
# ============================================================
OLD_BAR = re.search(
    r'<div class="tab-bar">.*?</div>\s*(?=\n\s*<!-- \(한국)',
    h, re.DOTALL
)
if not OLD_BAR:
    # fallback: 첫 번째 tab-bar 제거 대상 찾기
    OLD_BAR = re.search(r'<div class="tab-bar">.*?</div>\s*\n\s*<div id="tab-insight"', h, re.DOTALL)
if not OLD_BAR:
    raise RuntimeError("tab-bar 앵커 못찾음")

old_text = OLD_BAR.group()
# 정확히 tab-bar div만 추출 (뒤 lookahead 제외)
# 탭바 끝은 </div>\s*</div> 로 끝나는 첫 위치
bar_start = h.find('<div class="tab-bar">')
# depth counting으로 tab-bar 종료 찾기
depth = 0
i = bar_start
div_re = re.compile(r'<div\b|</div>')
bar_end = None
for m in div_re.finditer(h, i):
    if m.group() == '</div>':
        depth -= 1
        if depth == 0:
            bar_end = m.end()
            break
    else:
        depth += 1

NEW_BAR = """<div class="tab-bar">
  <button class="tab-btn active" data-tab="tab-growth" onclick="switchTab('tab-growth')">
    <span class="tab-badge">1</span> 25년 성장 게임 (광고/연령)
  </button>
  <button class="tab-btn" data-tab="tab-newgame" onclick="switchTab('tab-newgame')">
    <span class="tab-badge">2</span> 신규 진입 게임 분석
  </button>
</div>"""

h = h[:bar_start] + NEW_BAR + h[bar_end:]

# ============================================================
# 2) 깊이 카운팅 헬퍼 — 주어진 <div 시작 위치에서 매칭되는 </div> 끝 위치 반환
# ============================================================
def find_div_end(text, start):
    """text[start]는 '<div'로 시작해야 함. 매칭되는 </div> end+1 반환."""
    depth = 0
    i = start
    div_re = re.compile(r'<div\b|</div>')
    for m in div_re.finditer(text, i):
        if m.group() == '</div>':
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
    raise RuntimeError("matching </div> not found from " + str(start))

# ============================================================
# 3) 제거할 panel 목록
# ============================================================
REMOVE_IDS = ['tab-insight', 'tab-country-deep', 'tab-criteria', 'tab-webboard']

for tid in REMOVE_IDS:
    anchor = f'<div id="{tid}"'
    start = h.find(anchor)
    if start == -1:
        print(f"  [skip] {tid} 못찾음")
        continue
    end = find_div_end(h, start)
    # 앞뒤 주변 주석도 같이 제거 (예: "<!-- ===== TAB X: 이름 ===== -->\n")
    # 주석은 패널 바로 앞에 있을 수 있음
    comment_re = re.compile(r'<!--[^\n]*-->\s*\n\s*$')
    line_before = h.rfind('\n', 0, start)
    prev_text = h[line_before+1:start] if line_before > -1 else ''
    # 주석 붙어있으면 같이 지움
    if '<!--' in prev_text:
        start = line_before + 1
    removed = h[start:end]
    print(f"  [{tid}] 제거 {end-start}자, <div>={removed.count('<div')}, </div>={removed.count('</div>')}")
    # 뒤따르는 공백/줄바꿈도 같이 제거
    while end < len(h) and h[end] in ' \n\t':
        end += 1
    h = h[:start] + h[end:]

# ============================================================
# 4) tab-growth를 active로
# ============================================================
h = re.sub(
    r'<div id="tab-growth" class="tab-content(?:\s+active)?">',
    '<div id="tab-growth" class="tab-content active">',
    h, count=1
)

# ============================================================
# 5) 검증 + 저장
# ============================================================
n_open = h.count('<div'); n_close = h.count('</div>')
print(f"\n[결과] <div>={n_open}, </div>={n_close}  {'✅' if n_open==n_close else '❌'}")

with open(DST, 'w', encoding='utf-8') as f: f.write(h)
print(f"[저장] {DST}")

# 파일 크기
import os
print(f"[크기] {os.path.getsize(DST)/1024:.1f} KB (원본 {os.path.getsize(SRC)/1024:.1f} KB)")
