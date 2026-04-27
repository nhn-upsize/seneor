# -*- coding: utf-8 -*-
import re

# Step 1: newgame_entry_survival.html body·style 추출
with open('reports/newgame_entry_survival.html','r',encoding='utf-8') as f:
    src = f.read()

body_match = re.search(r'<body>(.*?)</body>', src, re.DOTALL)
body_content = body_match.group(1).strip()

style_match = re.search(r'<style>(.*?)</style>', src, re.DOTALL)
style_content = style_match.group(1).strip()

# 제목 "KR 시장"으로 변경
body_content = body_content.replace(
    '<h1>한국시장 매출 TOP100 — 신규 진입 &amp; 3개월 생존 분석</h1>',
    '<h1>KR 시장</h1>'
).replace(
    '<h1>한국시장 매출 TOP100 — 신규 진입 & 3개월 생존 분석</h1>',
    '<h1>KR 시장</h1>'
)

# Step 2: 메인 HTML 읽기
with open('reports/NHN_market_analysis.html','r',encoding='utf-8') as f:
    main = f.read()

lines = main.split('\n')

start_idx = None
for i, ln in enumerate(lines):
    if '<div id="tab-newgame" class="tab-content">' in ln:
        start_idx = i
        break

depth = 0
end_idx = None
for i in range(start_idx, len(lines)):
    ln = lines[i]
    depth += ln.count('<div')
    depth -= ln.count('</div>')
    if depth == 0 and i > start_idx:
        end_idx = i
        break

print(f'tab-newgame: line {start_idx+1} ~ {end_idx+1}')

new_content = '''<div id="tab-newgame" class="tab-content">
<div class="tab-newgame">

<style>
.tab-newgame { padding: 40px 24px; background: #f5f7fa; }
.tab-newgame .ng-subtab-bar { max-width: 1200px; margin: 0 auto 20px; display: flex; gap: 8px; border-bottom: 2px solid #e2e8f0; padding: 0 20px; }
.tab-newgame .ng-subtab-btn { background: none; border: none; padding: 10px 20px; font-family: inherit; font-size: 0.88rem; font-weight: 600; color: #64748b; cursor: pointer; border-bottom: 3px solid transparent; margin-bottom: -2px; display: flex; align-items: center; gap: 8px; }
.tab-newgame .ng-subtab-btn:hover { color: #0f172a; }
.tab-newgame .ng-subtab-btn.active { color: #0f172a; border-bottom-color: #0085ca; }
.tab-newgame .ng-subtab-btn .flag { font-size: 1.1rem; }
.tab-newgame .ng-panel { display: none; }
.tab-newgame .ng-panel.active { display: block; }
.tab-newgame .ng-empty { max-width: 1100px; margin: 40px auto; padding: 80px 24px; text-align: center; background: #fff; border-radius: 12px; border: 2px dashed #cbd5e1; color: #94a3b8; font-size: 0.9rem; }
''' + style_content + '''
</style>

<div class="ng-subtab-bar">
  <button class="ng-subtab-btn active" data-ng="kr" onclick="swNgTab('kr')"><span class="flag">🇰🇷</span>KR 시장</button>
  <button class="ng-subtab-btn" data-ng="jp" onclick="swNgTab('jp')"><span class="flag">🇯🇵</span>JP 시장</button>
  <button class="ng-subtab-btn" data-ng="us" onclick="swNgTab('us')"><span class="flag">🇺🇸</span>US 시장</button>
</div>

<div class="ng-panel active" id="ng-kr">
''' + body_content + '''
</div>

<div class="ng-panel" id="ng-jp">
  <div class="ng-empty">🇯🇵 JP 시장 신규 진입 분석 — 준비 중</div>
</div>

<div class="ng-panel" id="ng-us">
  <div class="ng-empty">🇺🇸 US 시장 신규 진입 분석 — 준비 중</div>
</div>

<script>
function swNgTab(id) {
  var container = document.getElementById('tab-newgame');
  if (!container) return;
  container.querySelectorAll('.ng-panel').forEach(p => p.classList.remove('active'));
  container.querySelectorAll('.ng-subtab-btn').forEach(b => b.classList.remove('active'));
  var panel = document.getElementById('ng-' + id);
  if (panel) panel.classList.add('active');
  var btn = container.querySelector('.ng-subtab-btn[data-ng="' + id + '"]');
  if (btn) btn.classList.add('active');
}
</script>

</div>
</div>'''

new_lines = lines[:start_idx] + [new_content] + lines[end_idx+1:]
with open('reports/NHN_market_analysis.html','w',encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print(f'완료. 라인수 {len(new_lines)}')
