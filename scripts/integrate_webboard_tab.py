# -*- coding: utf-8 -*-
"""
NHN_webboard_analysis.html 을 NHN_market_analysis.html 의 새 탭(tab-webboard)으로 통합.

- webboard CSS를 .tab-webboard 로 네임스페이스
- webboard body 콘텐츠를 <div id="tab-webboard" class="tab-content"> 안에 삽입
- 탭 바에 "5. 웹보드 심층분석" 버튼 추가
- 추가 CSS 변수(--neowiz/--up/--dn/--col26)는 .tab-webboard 로컬로 주입
"""
import os, re

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WEBBOARD = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"
BACKUP = MAIN + ".bak.before_webboard_tab"

# ============================================================
# 1) 파일 로드
# ============================================================
with open(MAIN, 'r', encoding='utf-8') as f: main = f.read()
with open(WEBBOARD, 'r', encoding='utf-8') as f: wb = f.read()

if not os.path.exists(BACKUP):
    with open(BACKUP, 'w', encoding='utf-8') as f: f.write(main)

main_orig_open = main.count('<div')
main_orig_close = main.count('</div>')
print(f"[BEFORE main] <div>={main_orig_open}, </div>={main_orig_close}")

# ============================================================
# 2) webboard의 <style>...</style> 추출
# ============================================================
wb_style_m = re.search(r'<style>(.*?)</style>', wb, re.DOTALL)
if not wb_style_m: raise RuntimeError("webboard <style> 못찾음")
wb_css = wb_style_m.group(1)

# ============================================================
# 3) CSS 네임스페이싱
#    - @import 제거 (main에 이미 있음)
#    - :root 제거 (필요한 vars만 .tab-webboard 안에서 재정의)
#    - * {..} 제거 (전역 리셋은 main꺼 사용)
#    - body {..} 제거
#    - 그 외 모든 규칙 앞에 ".tab-webboard " 를 prepend
# ============================================================
def namespace_css(css, ns='.tab-webboard'):
    # 주석 유지, 블록 단위 파싱
    out = []
    i = 0
    n = len(css)
    # @import 제거
    css = re.sub(r'@import[^;]*;', '', css)
    n = len(css)
    i = 0
    while i < n:
        # skip whitespace
        while i < n and css[i] in ' \t\r\n':
            out.append(css[i]); i += 1
        if i >= n: break
        # @-rule (e.g., @media, @keyframes) — treat block as-is but recursively prefix inside
        if css[i] == '@':
            # find matching { ... } or ;
            end_semi = css.find(';', i)
            end_brace = css.find('{', i)
            if end_brace == -1 or (end_semi != -1 and end_semi < end_brace):
                # statement at-rule
                j = end_semi + 1
                out.append(css[i:j]); i = j
                continue
            # block at-rule — find matching closing brace
            depth = 0
            j = end_brace
            while j < n:
                if css[j] == '{': depth += 1
                elif css[j] == '}':
                    depth -= 1
                    if depth == 0: break
                j += 1
            header = css[i:end_brace+1]
            body = css[end_brace+1:j]
            nested = namespace_css(body, ns)
            out.append(header + nested + '}')
            i = j + 1
            continue
        # ordinary rule: "selectors { ... }"
        end_brace = css.find('{', i)
        if end_brace == -1:
            out.append(css[i:]); break
        # find matching closing brace (handle nested via CSS not common, skip)
        depth = 0
        j = end_brace
        while j < n:
            if css[j] == '{': depth += 1
            elif css[j] == '}':
                depth -= 1
                if depth == 0: break
            j += 1
        selectors_raw = css[i:end_brace].strip()
        body = css[end_brace+1:j]
        # skip global-only selectors
        skip = False
        sel_list = [s.strip() for s in selectors_raw.split(',')]
        new_sels = []
        for s in sel_list:
            if not s: continue
            if s == '*': skip = True; break
            if s == 'body': skip = True; break
            if s == ':root': skip = True; break
            # 이미 네임스페이스 포함(드물지만) 체크
            new_sels.append(f'{ns} {s}')
        if skip:
            i = j + 1
            continue
        out.append(', '.join(new_sels) + ' {' + body + '}')
        i = j + 1
    return ''.join(out)

namespaced = namespace_css(wb_css)

# 추가 CSS 변수를 .tab-webboard 로컬 스코프에 정의
local_vars = """
  .tab-webboard {
    --neowiz: #ff6b35;
    --up: #059669;
    --dn: #dc2626;
    --col26: #fef3c7;
  }
"""
# webboard body 기본 설정(.tab-webboard 컨테이너에 padding 주기)
wrap_style = """
  .tab-webboard { padding: 32px 24px; background: var(--bg); }
"""

new_css_block = (
    "\n  /* ===== TAB 5: 웹보드 심층분석 (webboard namespaced) ===== */\n"
    + local_vars
    + wrap_style
    + namespaced
    + "\n  /* ===== end TAB 5 ===== */\n"
)

# main의 </style> 직전에 삽입
if '</style>' not in main: raise RuntimeError("main </style> 못찾음")
main = main.replace('</style>', new_css_block + '</style>', 1)

# ============================================================
# 4) webboard body 콘텐츠 추출
# ============================================================
wb_body_m = re.search(r'<body>(.*?)</body>', wb, re.DOTALL)
if not wb_body_m: raise RuntimeError("webboard <body> 못찾음")
wb_body = wb_body_m.group(1).strip()

# ============================================================
# 5) 탭 버튼 추가 — "데이터 기준 명세" 뒤
# ============================================================
OLD_TAB_BAR = '''  <button class="tab-btn" data-tab="tab-criteria" onclick="switchTab('tab-criteria')">
    <span class="tab-badge">4</span> 데이터 기준 명세
  </button>
</div>'''
NEW_TAB_BAR = '''  <button class="tab-btn" data-tab="tab-criteria" onclick="switchTab('tab-criteria')">
    <span class="tab-badge">4</span> 데이터 기준 명세
  </button>
  <button class="tab-btn" data-tab="tab-webboard" onclick="switchTab('tab-webboard')">
    <span class="tab-badge">5</span> 웹보드 심층분석
  </button>
</div>'''
if OLD_TAB_BAR not in main: raise RuntimeError("탭 바 앵커 못찾음")
main = main.replace(OLD_TAB_BAR, NEW_TAB_BAR, 1)

# 탭 badge 색상도 추가
BADGE_ANCHOR = '.tab-btn[data-tab="tab-newgame"] .tab-badge { background: #0f172a; }'
BADGE_NEW = BADGE_ANCHOR + '\n  .tab-btn[data-tab="tab-webboard"] .tab-badge { background: #0085ca; }'
if BADGE_ANCHOR in main:
    main = main.replace(BADGE_ANCHOR, BADGE_NEW, 1)

# ============================================================
# 6) 탭 콘텐츠 패널 삽입 — <script> 직전
# ============================================================
panel_html = (
    '\n<!-- ===== TAB 5: 웹보드 심층분석 ===== -->\n'
    '<div id="tab-webboard" class="tab-content">\n'
    '<div class="tab-webboard">\n'
    + wb_body + '\n'
    '</div>\n'
    '</div>\n'
)

SCRIPT_ANCHOR = '<!-- ===== JavaScript ===== -->'
if SCRIPT_ANCHOR not in main: raise RuntimeError("script 앵커 못찾음")
main = main.replace(SCRIPT_ANCHOR, panel_html + '\n' + SCRIPT_ANCHOR, 1)

# ============================================================
# 7) 저장 + div 밸런스 검증
# ============================================================
with open(MAIN, 'w', encoding='utf-8') as f: f.write(main)

new_open = main.count('<div')
new_close = main.count('</div>')
print(f"[AFTER main] <div>={new_open}, </div>={new_close}  delta={new_open-new_close}")
print(f"[DIFF] 추가: +{new_open-main_orig_open} <div>, +{new_close-main_orig_close} </div>")
if new_open == new_close:
    print("  ✅ div 밸런스 OK")
else:
    print("  ❌ div 불균형!")
print("[DONE]", MAIN)
print("[BACKUP]", BACKUP)
