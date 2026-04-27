#!/usr/bin/env python3
"""Merge newgame analysis tab into main HTML"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_newgame_analysis.html','r',encoding='utf-8') as f:
    new_html = f.read()

with open(r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html','r',encoding='utf-8') as f:
    main_html = f.read()

# Extract container content
container_match = re.search(r'<div class="container">(.*?)</div>\s*<script>', new_html, re.DOTALL)
container_content = container_match.group(1) if container_match else ''

# Namespaced CSS for tab-newgame
namespaced_css = """
  /* ===== Tab: 신규 진입 게임 분석 ===== */
  .tab-newgame { padding: 32px 24px; background: #fafbfc; }
  .tab-newgame .ng-container { max-width: 1300px; margin: 0 auto; }
  .tab-newgame h1 { font-size: 1.6rem; font-weight: 800; text-align: center; margin-bottom: 6px; }
  .tab-newgame .ng-subtitle { text-align: center; font-size: 0.82rem; color: #94a3b8; margin-bottom: 32px; }
  .tab-newgame .ng-definition { background: #fef3c7; border: 1px solid #fbbf24; border-left: 4px solid #f59e0b; border-radius: 10px; padding: 16px 20px; margin-bottom: 28px; font-size: 0.8rem; color: #78350f; line-height: 1.7; }
  .tab-newgame .ng-section { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
  .tab-newgame .ng-section-head { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
  .tab-newgame .ng-section-num { width: 32px; height: 32px; border-radius: 8px; color: #fff; font-size: 0.85rem; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; background: #0f172a; }
  .tab-newgame .ng-section h2 { font-size: 1.05rem; font-weight: 700; }
  .tab-newgame .ng-desc { font-size: 0.78rem; color: #475569; margin-top: 4px; line-height: 1.5; }
  .tab-newgame .ng-os-tabs { display: flex; gap: 4px; border-bottom: 2px solid #e2e8f0; margin-bottom: 16px; }
  .tab-newgame .ng-os-tab { padding: 8px 20px; border: none; background: none; cursor: pointer; font-size: 0.82rem; font-weight: 600; color: #94a3b8; border-bottom: 3px solid transparent; margin-bottom: -2px; font-family: inherit; }
  .tab-newgame .ng-os-tab.active { color: #1e293b; border-bottom-color: #0f172a; }
  .tab-newgame .ng-os-content { display: none; }
  .tab-newgame .ng-os-content.active { display: block; }
  .tab-newgame table { width: 100%; border-collapse: collapse; font-size: 0.76rem; }
  .tab-newgame th { background: #f1f5f9; padding: 9px 12px; text-align: left; font-weight: 700; border-bottom: 2px solid #e2e8f0; color: #475569; }
  .tab-newgame th.r, .tab-newgame td.r { text-align: right; }
  .tab-newgame td { padding: 8px 12px; border-bottom: 1px solid #f1f5f9; color: #475569; }
  .tab-newgame td.name { font-weight: 700; color: #1e293b; }
  .tab-newgame .ng-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .tab-newgame .ng-country-card { border-radius: 10px; padding: 16px 18px; }
  .tab-newgame .ng-country-card.kr { background: #eff6ff; border: 1px solid #bfdbfe; }
  .tab-newgame .ng-country-card.jp { background: #fef2f2; border: 1px solid #fecaca; }
  .tab-newgame .ng-country-card.us { background: #faf5ff; border: 1px solid #d8b4fe; }
  .tab-newgame .ng-country-title { font-size: 0.88rem; font-weight: 800; margin-bottom: 10px; }
  .tab-newgame .ng-country-title.kr { color: #1e40af; }
  .tab-newgame .ng-country-title.jp { color: #b91c1c; }
  .tab-newgame .ng-country-title.us { color: #6b21a8; }
  .tab-newgame .ng-num { font-variant-numeric: tabular-nums; text-align: right; }
  .tab-newgame .ng-up { color: #059669; font-weight: 700; }
  .tab-newgame .ng-dn { color: #dc2626; font-weight: 700; }
  .tab-newgame .ng-ins { font-size: 0.78rem; color: #475569; margin-top: 12px; padding: 10px 14px; background: #f8fafc; border-radius: 8px; border-left: 3px solid #0f172a; line-height: 1.7; }
  .tab-newgame .ng-ins strong { color: #1e293b; }
  .tab-newgame .ng-bar-bg { width: 100%; height: 20px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
  .tab-newgame .ng-bar-fill { height: 100%; display: flex; align-items: center; padding: 0 8px; color: #fff; font-size: 0.7rem; font-weight: 700; }
  .tab-newgame .ng-bar-fill.kr { background: #3b82f6; }
  .tab-newgame .ng-bar-fill.jp { background: #ef4444; }
  .tab-newgame .ng-bar-fill.us { background: #a855f7; }
  .tab-newgame .ng-bar-fill.cn { background: #f59e0b; }
  .tab-newgame .ng-bar-fill.na { background: #8b5cf6; }
  .tab-newgame .ng-bar-fill.etc { background: #6b7280; }
  .tab-newgame .ng-bar-fill.survived { background: #059669; }
  .tab-newgame svg { width: 100%; max-width: 100%; height: auto; display: block; }
  .tab-newgame .ng-legend { display: flex; gap: 16px; justify-content: center; margin-top: 8px; font-size: 0.72rem; }
  .tab-newgame .ng-legend-item { display: flex; align-items: center; gap: 6px; }
  .tab-newgame .ng-legend-dot { width: 10px; height: 10px; border-radius: 2px; }
  .tab-newgame .ng-footer { text-align: center; font-size: 0.7rem; color: #94a3b8; padding: 20px 0; }
  .tab-btn[data-tab="tab-newgame"] .tab-badge { background: #0f172a; }
"""

main_html = main_html.replace('</style>', namespaced_css + '\n</style>', 1)
print('CSS added')

# Class name mapping (add ng- prefix)
ng_body = container_content
class_map = [
    ('class="container"', 'class="ng-container"'),
    ('class="subtitle"', 'class="ng-subtitle"'),
    ('class="definition"', 'class="ng-definition"'),
    ('class="section"', 'class="ng-section"'),
    ('class="section-head"', 'class="ng-section-head"'),
    ('class="section-num"', 'class="ng-section-num"'),
    ('class="desc"', 'class="ng-desc"'),
    ('class="os-tabs"', 'class="ng-os-tabs"'),
    ('class="os-tab', 'class="ng-os-tab'),
    ('class="os-content"', 'class="ng-os-content"'),
    ('class="os-content active"', 'class="ng-os-content active"'),
    ('id="os-', 'id="ng-os-'),
    ('class="grid-3"', 'class="ng-grid-3"'),
    ('class="country-card', 'class="ng-country-card'),
    ('class="country-title', 'class="ng-country-title'),
    ('class="num"', 'class="ng-num"'),
    ('class="ins"', 'class="ng-ins"'),
    ('class="bar-bg"', 'class="ng-bar-bg"'),
    ('class="bar-fill', 'class="ng-bar-fill'),
    ('class="legend"', 'class="ng-legend"'),
    ('class="legend-item"', 'class="ng-legend-item"'),
    ('class="legend-dot"', 'class="ng-legend-dot"'),
    ('class="footer"', 'class="ng-footer"'),
    ('class="up"', 'class="ng-up"'),
    ('class="dn"', 'class="ng-dn"'),
    ('class="r up"', 'class="r ng-up"'),
    ('class="r dn"', 'class="r ng-dn"'),
]
for old, new in class_map:
    ng_body = ng_body.replace(old, new)

ng_body = ng_body.replace('onclick="switchOS(', 'onclick="switchNgOS(')
ng_body = ng_body.replace("document.getElementById('os-", "document.getElementById('ng-os-")

# Add tab button before tab-criteria
new_button = '''  <button class="tab-btn" data-tab="tab-newgame" onclick="switchTab('tab-newgame')">
    <span class="tab-badge">3</span> 신규 진입 게임 분석
  </button>
'''
main_html = main_html.replace(
    '  <button class="tab-btn" data-tab="tab-criteria"',
    new_button + '  <button class="tab-btn" data-tab="tab-criteria"',
    1
)
print('Tab button added')

# Renumber 데이터 기준 명세 to 4
main_html = main_html.replace(
    '<span class="tab-badge">3</span> 데이터 기준 명세',
    '<span class="tab-badge">4</span> 데이터 기준 명세',
    1
)

# Insert new tab content before tab-criteria
new_tab_html = f'''
<!-- ===== TAB 3: 신규 진입 게임 분석 ===== -->
<div id="tab-newgame" class="tab-content">
<div class="tab-newgame">
{ng_body}
</div>
</div>

'''

target = '<!-- ===== TAB 3: 데이터 기준 명세 ====='
if target in main_html:
    main_html = main_html.replace(target, new_tab_html + '<!-- ===== TAB 4: 데이터 기준 명세 =====', 1)
    print('Inserted new tab content')
else:
    target2 = '<div id="tab-criteria"'
    pos = main_html.find(target2)
    if pos > 0:
        # Find marker before
        marker_pos = main_html.rfind('<!-- ===== TAB', 0, pos)
        if marker_pos > 0:
            main_html = main_html[:marker_pos] + new_tab_html + main_html[marker_pos:]
            print('Inserted new tab content (alt)')

# Add switchNgOS function
new_func = """
function switchNgOS(btn, section, os) {
  var tabs = btn.parentElement.querySelectorAll('.ng-os-tab');
  tabs.forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  var contents = document.querySelectorAll('[id^="ng-os-' + section + '-"]');
  contents.forEach(c => c.classList.remove('active'));
  var target = document.getElementById('ng-os-' + section + '-' + os);
  if (target) target.classList.add('active');
}
"""
main_html = main_html.replace('</script>', new_func + '\n</script>', 1)
print('switchNgOS function added')

# Verify
d = main_html.count('<div')
c = main_html.count('</div>')
print(f'\ndiv: {d}/{c} diff={d-c}')

panels = ['tab-insight','tab-growth','tab-newgame','tab-criteria','tab-country-deep']
for name in panels:
    pos = main_html.find(f'id="{name}"')
    if pos > 0:
        before = main_html[:pos]
        opens = len(re.findall(r'<div[\s>]', before))
        closes = before.count('</div>')
        print(f'{name}: depth before = {opens - closes}')

with open(r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html','w',encoding='utf-8') as f:
    f.write(main_html)
print('\nDone!')
