#!/usr/bin/env python3
"""
Apply all restoration tasks to NHN_market_analysis.html.
Verify div balance after each task. Save only when balanced.

Tasks:
1. Extract tab-analysis (A~G) to standalone file, remove from main
2. (Tab-growth already present - skip)
3. Add DART OP inline under each year cell in Step star table
4. Add rank + concentration sections before conclusion kr
5. Add quarterly chart + seasonality insights in each country panel (before conclusion)
6. Add CN share chart in ALL panel between Step 2 and Step 3
7. Renumber tabs and update CSS
"""
import sys, io, re, os, shutil, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
AG_OUT = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_AG_analysis_tree.html"

def verify(html, label):
    o = html.count('<div')
    c = html.count('</div>')
    print(f"  [{label}] div open={o} close={c} diff={o-c}")
    if o != c:
        raise RuntimeError(f"DIV UNBALANCED at {label}: open={o}, close={c}")
    return True

def read_html():
    with open(MAIN, 'r', encoding='utf-8') as f:
        return f.read()

def write_html(html):
    with open(MAIN, 'w', encoding='utf-8') as f:
        f.write(html)

# =========================================================
# Task 1: Extract A~G tab to standalone file + remove from main
# =========================================================
def task1_extract_ag(html):
    print("\n=== Task 1: Extract A~G analysis tab ===")

    # Find CSS block: from /* ===== Tab 2: market_research_mindmap styles ===== */
    # up to next /* ===== Tab
    css_start_m = re.search(r'  /\* ===== Tab 2: market_research_mindmap styles ===== \*/', html)
    if not css_start_m:
        raise RuntimeError("Tab 2 CSS marker not found")
    css_start = css_start_m.start()
    # Next /* ===== marker
    css_end_m = re.search(r'  /\* ===== Tab 3: data_criteria', html[css_start+10:])
    if not css_end_m:
        raise RuntimeError("Tab 3 criteria CSS marker not found after Tab 2")
    css_end = css_start + 10 + css_end_m.start()
    tab2_css = html[css_start:css_end]
    print(f"  CSS block: {css_end-css_start} bytes")

    # Also grab root shared CSS (:root and body) for standalone file - copy from start
    # Find the <style>..</style> start
    shared_css_start = html.find('<style>') + len('<style>')
    # Up to .tab-analysis (Tab 2)
    shared_end = css_start
    shared_css = html[shared_css_start:shared_end]

    # Find tab content: <!-- ===== TAB 2: A~G 분석 트리 & 결과 ===== --> to end of </div>\n</div>
    tab_start_marker = '<!-- ===== TAB 2: A~G 분석 트리 &amp; 결과 ===== -->'
    tab_start = html.find(tab_start_marker)
    if tab_start < 0:
        # try alt
        tab_start = html.find('<!-- ===== TAB 2: A~G')
    if tab_start < 0:
        raise RuntimeError("tab-analysis start marker not found")

    # Find end: the closing pattern ends right before <!-- ===== TAB 3: 25년 성장 게임
    tab_end_marker = '<!-- ===== TAB 3: 25년 성장 게임'
    tab_end = html.find(tab_end_marker)
    if tab_end < 0:
        raise RuntimeError("tab-growth marker not found (end of tab-analysis)")

    tab_html = html[tab_start:tab_end]
    print(f"  Tab content: {len(tab_html)} bytes")

    # Verify div balance within the extracted block
    o = tab_html.count('<div')
    c = tab_html.count('</div>')
    print(f"  Extracted tab div balance: open={o} close={c}")

    # JS extraction: we need toggleBranch, toggleL2, toggleAll, toggleAcc, toggleAllAcc
    js_snippets = '''
// Tree toggle
function toggleBranch(id) {
  document.getElementById(id).classList.toggle('open');
}
function toggleL2(el) {
  el.classList.toggle('open');
  event.stopPropagation();
}
let allOpen = false;
function toggleAll() {
  allOpen = !allOpen;
  document.querySelectorAll('.tab-analysis .branch').forEach(b => {
    allOpen ? b.classList.add('open') : b.classList.remove('open');
  });
  document.querySelectorAll('.tab-analysis .l2-node').forEach(n => {
    allOpen ? n.classList.add('open') : n.classList.remove('open');
  });
}
function toggleAcc(el) { el.classList.toggle('open'); }
let accAllOpen = false;
function toggleAllAcc() {
  accAllOpen = !accAllOpen;
  document.querySelectorAll('.tab-analysis .acc-header').forEach(h => {
    accAllOpen ? h.classList.add('open') : h.classList.remove('open');
  });
}
'''

    # Build standalone file
    # tab_html starts with <!-- ... --> then <div id="tab-analysis" class="tab-content">
    # strip outer <div id="tab-analysis" class="tab-content"> wrapper, keep inside
    inner_start = tab_html.find('<div id="tab-analysis"')
    inner = tab_html[inner_start:]  # from <div id="tab-analysis">

    standalone = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NHN 시장 분석 — A~G 분석 트리</title>
<style>
{shared_css}
{tab2_css}
  /* Standalone override: always show tab-analysis */
  #tab-analysis {{ display: block !important; }}
</style>
</head>
<body>
{inner}
<script>
{js_snippets}
</script>
</body>
</html>
'''
    with open(AG_OUT, 'w', encoding='utf-8') as f:
        f.write(standalone)
    print(f"  Wrote {AG_OUT}: {len(standalone):,} bytes")
    # verify
    so = standalone.count('<div')
    sc = standalone.count('</div>')
    print(f"  Standalone div: open={so} close={sc} diff={so-sc}")

    # Remove tab-analysis from main html (the tab_html we extracted)
    html = html[:tab_start] + html[tab_end:]

    # Remove CSS block from main
    # Re-find after content removal (positions shifted, so we use fresh regex)
    html = re.sub(
        r'  /\* ===== Tab 2: market_research_mindmap styles ===== \*/.*?(?=  /\* ===== Tab 3: data_criteria)',
        '',
        html,
        count=1,
        flags=re.DOTALL
    )

    # Remove tab-analysis button from tab-bar
    html = re.sub(
        r'\s*<button class="tab-btn" data-tab="tab-analysis" onclick="switchTab\(\'tab-analysis\'\)">\s*'
        r'<span class="tab-badge">\d+</span>[^<]*A~G[^<]*\s*</button>\s*\n',
        '\n  ',
        html,
        count=1
    )

    # Remove .tab-btn[data-tab="tab-analysis"] CSS rule
    html = re.sub(
        r'\s*\.tab-btn\[data-tab="tab-analysis"\] \.tab-badge \{ background: [^;]+; \}',
        '',
        html,
        count=1
    )

    # Remove tree/accordion JS from main (it's now only in standalone)
    # Remove toggleBranch, toggleL2, allOpen, toggleAll, Accordion block
    html = re.sub(
        r'// Tree toggle \(Tab 2\).*?// Country tab switching',
        '// Country tab switching',
        html,
        count=1,
        flags=re.DOTALL
    )

    verify(html, "Task 1 done")
    return html

# =========================================================
# Task 3: Add DART OP inline
# =========================================================
DART = {
    '엔씨소프트':    {2022:5590, 2023:1373, 2024:-1092, 2025:161},
    '넷마블':        {2022:-1087, 2023:-685, 2024:2156, 2025:3525},
    '카카오게임즈':  {2022:1758, 2023:745, 2024:191, 2025:-396},
    'NHN':           {2022:391, 2023:556, 2024:-326, 2025:1324},
    '컴투스':        {2022:-167, 2023:-332, 2024:61, 2025:26},
    '위메이드':      {2022:-849, 2023:-1104, 2024:71, 2025:107},
    '데브시스터즈':  {2022:-199, 2023:-480, 2024:272, 2025:64},
    '크래프톤':      {2022:7516, 2023:7680, 2024:11825, 2025:10544},
    '네오위즈':      {2022:196, 2023:316, 2024:329, 2025:600},
    '웹젠':          {2022:830, 2023:499, 2024:546, 2025:297},
    '펄어비스':      {2022:164, 2023:-164, 2024:-123, 2025:-148},
}

def fmt_op(v):
    color = '#059669' if v >= 0 else '#dc2626'
    return f"<span style='color:{color};font-size:0.58rem;'>OP {v:,}</span>"

def task3_dart_inline(html):
    print("\n=== Task 3: DART OP inline ===")
    for pub_name, op_data in DART.items():
        search = f'<strong>{pub_name}</strong>'
        pos = html.find(search)
        if pos == -1:
            print(f"  SKIP: {pub_name} not found")
            continue
        tr_start = html.rfind('<tr', 0, pos)
        tr_end = html.find('</tr>', pos) + 5
        if tr_start == -1 or tr_end == -1:
            continue
        row = html[tr_start:tr_end]
        cells = list(re.finditer(r'(<td class="num[^"]*">)(\d[\d,]*)(</td>)', row))
        if len(cells) < 4:
            print(f"  WARN: {pub_name} has {len(cells)} cells")
            continue
        # Already processed? check if 'OP' already in this row
        if 'OP ' in row:
            print(f"  SKIP already done: {pub_name}")
            continue
        years = [2022, 2023, 2024, 2025]
        new_row = row
        for i in range(min(4, len(cells))):
            cell = cells[i]
            yr = years[i]
            if yr in op_data:
                op_str = fmt_op(op_data[yr])
                old_cell = cell.group(0)
                new_cell = f'{cell.group(1)}{cell.group(2)}<br>{op_str}{cell.group(3)}'
                new_row = new_row.replace(old_cell, new_cell, 1)
        html = html[:tr_start] + new_row + html[tr_end:]
        print(f"  OK: {pub_name}")
    verify(html, "Task 3 done")
    return html

# =========================================================
# Task 4: Add rank + concentration sections before conclusion kr
# =========================================================
RANK_SECTION = '''
  <!-- 매출 순위별 월평균 규모 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num" style="background:#475569;">&#x1F4CA;</div>
      <div class="step-info">
        <div class="step-q">국가별 매출 순위별 월평균 규모 (억원) <span style="font-size:0.7rem;color:#64748b;font-weight:500;">TOP100 내 1/10/20/50/100위</span></div>
        <div class="step-a">US 100위(68억) &asymp; KR 20위(62억). US 시장의 두께가 KR·JP 대비 압도적 — NHN 진출 시 <strong>중위권만 해도 KR 상위권 매출</strong></div>
      </div>
    </div>
    <div class="step-body">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">

        <!-- KR -->
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:14px;">
          <div style="font-size:0.82rem;font-weight:700;color:#1e40af;margin-bottom:10px;">&#x1F1F0;&#x1F1F7; KR 한국</div>
          <table style="width:100%;border-collapse:collapse;font-size:0.72rem;">
            <thead><tr><th style="text-align:left;padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">순위</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'22</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'23</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'24</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'25</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#fbbf24;color:#78350f;">26.1Q</th></tr></thead>
            <tbody>
              <tr><td style="padding:4px 6px;font-weight:600;">1위</td><td class="num" style="padding:4px 6px;">406</td><td class="num" style="padding:4px 6px;">476</td><td class="num" style="padding:4px 6px;">510</td><td class="num" style="padding:4px 6px;">605</td><td class="num" style="padding:4px 6px;background:#fef3c7;">487</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">10위</td><td class="num" style="padding:4px 6px;">105</td><td class="num" style="padding:4px 6px;">94</td><td class="num" style="padding:4px 6px;">105</td><td class="num" style="padding:4px 6px;">123</td><td class="num" style="padding:4px 6px;background:#fef3c7;">91</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">20위</td><td class="num" style="padding:4px 6px;">48</td><td class="num" style="padding:4px 6px;">59</td><td class="num" style="padding:4px 6px;">73</td><td class="num" style="padding:4px 6px;">64</td><td class="num" style="padding:4px 6px;background:#fef3c7;">46</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">50위</td><td class="num" style="padding:4px 6px;">25</td><td class="num" style="padding:4px 6px;">30</td><td class="num" style="padding:4px 6px;">31</td><td class="num" style="padding:4px 6px;">26</td><td class="num" style="padding:4px 6px;background:#fef3c7;">24</td></tr>
              <tr style="border-top:2px solid #93c5fd;"><td style="padding:4px 6px;font-weight:600;">100위</td><td class="num" style="padding:4px 6px;">14</td><td class="num" style="padding:4px 6px;">17</td><td class="num" style="padding:4px 6px;">18</td><td class="num" style="padding:4px 6px;">15</td><td class="num" style="padding:4px 6px;background:#fef3c7;">9</td></tr>
            </tbody>
          </table>
        </div>

        <!-- JP -->
        <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:14px;">
          <div style="font-size:0.82rem;font-weight:700;color:#b91c1c;margin-bottom:10px;">&#x1F1EF;&#x1F1F5; JP 일본</div>
          <table style="width:100%;border-collapse:collapse;font-size:0.72rem;">
            <thead><tr><th style="text-align:left;padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">순위</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'22</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'23</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'24</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'25</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fbbf24;color:#78350f;">26.1Q</th></tr></thead>
            <tbody>
              <tr><td style="padding:4px 6px;font-weight:600;">1위</td><td class="num" style="padding:4px 6px;">748</td><td class="num" style="padding:4px 6px;">640</td><td class="num" style="padding:4px 6px;">672</td><td class="num" style="padding:4px 6px;">470</td><td class="num" style="padding:4px 6px;background:#fef3c7;">433</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">10위</td><td class="num" style="padding:4px 6px;">218</td><td class="num" style="padding:4px 6px;">249</td><td class="num" style="padding:4px 6px;">235</td><td class="num" style="padding:4px 6px;">219</td><td class="num" style="padding:4px 6px;background:#fef3c7;">223</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">20위</td><td class="num" style="padding:4px 6px;">112</td><td class="num" style="padding:4px 6px;">143</td><td class="num" style="padding:4px 6px;">150</td><td class="num" style="padding:4px 6px;">135</td><td class="num" style="padding:4px 6px;background:#fef3c7;">131</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">50위</td><td class="num" style="padding:4px 6px;">63</td><td class="num" style="padding:4px 6px;">57</td><td class="num" style="padding:4px 6px;">62</td><td class="num" style="padding:4px 6px;">59</td><td class="num" style="padding:4px 6px;background:#fef3c7;">54</td></tr>
              <tr style="border-top:2px solid #fca5a5;"><td style="padding:4px 6px;font-weight:600;">100위</td><td class="num" style="padding:4px 6px;">38</td><td class="num" style="padding:4px 6px;">34</td><td class="num" style="padding:4px 6px;">35</td><td class="num" style="padding:4px 6px;">35</td><td class="num" style="padding:4px 6px;background:#fef3c7;">24</td></tr>
            </tbody>
          </table>
        </div>

        <!-- US -->
        <div style="background:#faf5ff;border:1px solid #d8b4fe;border-radius:10px;padding:14px;">
          <div style="font-size:0.82rem;font-weight:700;color:#6b21a8;margin-bottom:10px;">&#x1F1FA;&#x1F1F8; US 미국</div>
          <table style="width:100%;border-collapse:collapse;font-size:0.72rem;">
            <thead><tr><th style="text-align:left;padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">순위</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'22</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'23</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'24</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'25</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#fbbf24;color:#78350f;">26.1Q</th></tr></thead>
            <tbody>
              <tr><td style="padding:4px 6px;font-weight:600;">1위</td><td class="num" style="padding:4px 6px;">896</td><td class="num" style="padding:4px 6px;">1,681</td><td class="num" style="padding:4px 6px;">2,267</td><td class="num" style="padding:4px 6px;">1,793</td><td class="num" style="padding:4px 6px;background:#fef3c7;">1,483</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">10위</td><td class="num" style="padding:4px 6px;">278</td><td class="num" style="padding:4px 6px;">319</td><td class="num" style="padding:4px 6px;">412</td><td class="num" style="padding:4px 6px;">416</td><td class="num" style="padding:4px 6px;background:#fef3c7;">406</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">20위</td><td class="num" style="padding:4px 6px;">206</td><td class="num" style="padding:4px 6px;">194</td><td class="num" style="padding:4px 6px;">223</td><td class="num" style="padding:4px 6px;">267</td><td class="num" style="padding:4px 6px;background:#fef3c7;">222</td></tr>
              <tr><td style="padding:4px 6px;font-weight:600;">50위</td><td class="num" style="padding:4px 6px;">111</td><td class="num" style="padding:4px 6px;">107</td><td class="num" style="padding:4px 6px;">108</td><td class="num" style="padding:4px 6px;">118</td><td class="num" style="padding:4px 6px;background:#fef3c7;">111</td></tr>
              <tr style="border-top:2px solid #d8b4fe;"><td style="padding:4px 6px;font-weight:600;">100위</td><td class="num" style="padding:4px 6px;">57</td><td class="num" style="padding:4px 6px;">56</td><td class="num" style="padding:4px 6px;">61</td><td class="num" style="padding:4px 6px;">67</td><td class="num" style="padding:4px 6px;background:#fef3c7;">47</td></tr>
            </tbody>
          </table>
        </div>

      </div>
      <div class="ins" style="margin-top:14px;"><strong>핵심:</strong> US 100위(47~67억) &asymp; KR 20위(46~73억) 수준. <strong>US 시장은 100위권에서도 KR 상위권 매출을 기록</strong> &mdash; NHN 웹보드가 US 진출 시 중위권만 안착해도 KR 대비 3~4배 매출 잠재력. JP는 1위가 22년 748억&rarr;25년 470억으로 축소, 정체 시장 확인.</div>
      <div class="formula-box">
        <strong>&#x1F4D0; 정의/공식</strong><br>
        &bull; 기준: iOS+Android 합산 매출 TOP100 (in_revenue_top100_unified_os) 내 연도별 순위<br>
        &bull; 월평균 매출 = SUM(revenue_usd_100p &times; 연도별 환율) / 월수 (단위: 억원)<br>
        &bull; 순위: 해당 연도 내 월평균 매출 기준 내림차순
      </div>
    </div>
  </div>

  <!-- 매출 집중도 분석 (80/20 법칙) -->
  <div class="step">
    <div class="step-head">
      <div class="step-num" style="background:#7c3aed;">&#x1F50D;</div>
      <div class="step-info">
        <div class="step-q">매출 집중도 분석 &mdash; 80/20 법칙 검증 <span style="font-size:0.7rem;color:#64748b;font-weight:500;">TOP100 내 상위 N% 매출 비중</span></div>
        <div class="step-a"><strong>"50/80 법칙"에 가까움</strong> &mdash; 상위 20%(20개)가 약 55~63%, <strong>상위 50%(50개)가 약 80~86%</strong>. 전통적 80/20은 불일치. KR이 집중도 가장 높음</div>
      </div>
    </div>
    <div class="step-body">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">

        <!-- KR -->
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:14px;">
          <div style="font-size:0.82rem;font-weight:700;color:#1e40af;margin-bottom:10px;">&#x1F1F0;&#x1F1F7; KR &mdash; 집중도 <span style="color:#dc2626;">최고</span></div>
          <table style="width:100%;border-collapse:collapse;font-size:0.72rem;">
            <thead><tr><th style="text-align:left;padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">구간</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'22</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'23</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'24</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#dbeafe;">'25</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #93c5fd;background:#fbbf24;color:#78350f;">26.1Q</th></tr></thead>
            <tbody>
              <tr><td style="padding:4px 6px;">TOP 5 (5%)</td><td class="num" style="padding:4px 6px;">37.7</td><td class="num" style="padding:4px 6px;">31.8</td><td class="num" style="padding:4px 6px;">36.2</td><td class="num" style="padding:4px 6px;">32.5</td><td class="num" style="padding:4px 6px;background:#fef3c7;">33.5</td></tr>
              <tr><td style="padding:4px 6px;">TOP 10 (10%)</td><td class="num" style="padding:4px 6px;">49.5</td><td class="num" style="padding:4px 6px;">44.4</td><td class="num" style="padding:4px 6px;">48.6</td><td class="num" style="padding:4px 6px;">46.2</td><td class="num" style="padding:4px 6px;background:#fef3c7;">45.3</td></tr>
              <tr style="font-weight:600;"><td style="padding:4px 6px;color:#dc2626;">TOP 20 (20%)</td><td class="num" style="padding:4px 6px;">63.2</td><td class="num" style="padding:4px 6px;">60.4</td><td class="num" style="padding:4px 6px;">63.0</td><td class="num" style="padding:4px 6px;">62.6</td><td class="num" style="padding:4px 6px;background:#fef3c7;">60.3</td></tr>
              <tr style="font-weight:700;background:#dbeafe;"><td style="padding:4px 6px;color:#059669;">TOP 50 (50%)</td><td class="num" style="padding:4px 6px;">84.5</td><td class="num" style="padding:4px 6px;">83.9</td><td class="num" style="padding:4px 6px;">85.2</td><td class="num" style="padding:4px 6px;">86.1</td><td class="num" style="padding:4px 6px;background:#fef3c7;">84.8</td></tr>
            </tbody>
          </table>
        </div>

        <!-- JP -->
        <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:14px;">
          <div style="font-size:0.82rem;font-weight:700;color:#b91c1c;margin-bottom:10px;">&#x1F1EF;&#x1F1F5; JP &mdash; 집중도 하락 추세</div>
          <table style="width:100%;border-collapse:collapse;font-size:0.72rem;">
            <thead><tr><th style="text-align:left;padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">구간</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'22</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'23</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'24</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fee2e2;">'25</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #fca5a5;background:#fbbf24;color:#78350f;">26.1Q</th></tr></thead>
            <tbody>
              <tr><td style="padding:4px 6px;">TOP 5 (5%)</td><td class="num" style="padding:4px 6px;">30.8</td><td class="num" style="padding:4px 6px;">26.2</td><td class="num" style="padding:4px 6px;">21.1</td><td class="num" style="padding:4px 6px;">22.8</td><td class="num" style="padding:4px 6px;background:#fef3c7;">20.1</td></tr>
              <tr><td style="padding:4px 6px;">TOP 10 (10%)</td><td class="num" style="padding:4px 6px;">45.1</td><td class="num" style="padding:4px 6px;">39.8</td><td class="num" style="padding:4px 6px;">34.9</td><td class="num" style="padding:4px 6px;">36.6</td><td class="num" style="padding:4px 6px;background:#fef3c7;">34.2</td></tr>
              <tr style="font-weight:600;"><td style="padding:4px 6px;color:#dc2626;">TOP 20 (20%)</td><td class="num" style="padding:4px 6px;">60.9</td><td class="num" style="padding:4px 6px;">57.4</td><td class="num" style="padding:4px 6px;">54.1</td><td class="num" style="padding:4px 6px;">54.8</td><td class="num" style="padding:4px 6px;background:#fef3c7;">52.4</td></tr>
              <tr style="font-weight:700;background:#fee2e2;"><td style="padding:4px 6px;color:#059669;">TOP 50 (50%)</td><td class="num" style="padding:4px 6px;">82.7</td><td class="num" style="padding:4px 6px;">82.6</td><td class="num" style="padding:4px 6px;">81.9</td><td class="num" style="padding:4px 6px;">81.6</td><td class="num" style="padding:4px 6px;background:#fef3c7;">82.0</td></tr>
            </tbody>
          </table>
        </div>

        <!-- US -->
        <div style="background:#faf5ff;border:1px solid #d8b4fe;border-radius:10px;padding:14px;">
          <div style="font-size:0.82rem;font-weight:700;color:#6b21a8;margin-bottom:10px;">&#x1F1FA;&#x1F1F8; US &mdash; 집중도 <span style="color:#059669;">상승 중</span></div>
          <table style="width:100%;border-collapse:collapse;font-size:0.72rem;">
            <thead><tr><th style="text-align:left;padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">구간</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'22</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'23</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'24</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#f3e8ff;">'25</th><th class="num" style="padding:4px 6px;border-bottom:2px solid #d8b4fe;background:#fbbf24;color:#78350f;">26.1Q</th></tr></thead>
            <tbody>
              <tr><td style="padding:4px 6px;">TOP 5 (5%)</td><td class="num" style="padding:4px 6px;">20.1</td><td class="num" style="padding:4px 6px;">27.7</td><td class="num" style="padding:4px 6px;">33.7</td><td class="num" style="padding:4px 6px;">29.0</td><td class="num" style="padding:4px 6px;background:#fef3c7;">28.2</td></tr>
              <tr><td style="padding:4px 6px;">TOP 10 (10%)</td><td class="num" style="padding:4px 6px;">30.9</td><td class="num" style="padding:4px 6px;">38.7</td><td class="num" style="padding:4px 6px;">45.1</td><td class="num" style="padding:4px 6px;">40.0</td><td class="num" style="padding:4px 6px;background:#fef3c7;">41.4</td></tr>
              <tr style="font-weight:600;"><td style="padding:4px 6px;color:#dc2626;">TOP 20 (20%)</td><td class="num" style="padding:4px 6px;">47.3</td><td class="num" style="padding:4px 6px;">53.9</td><td class="num" style="padding:4px 6px;">59.6</td><td class="num" style="padding:4px 6px;">56.7</td><td class="num" style="padding:4px 6px;background:#fef3c7;">57.4</td></tr>
              <tr style="font-weight:700;background:#f3e8ff;"><td style="padding:4px 6px;color:#059669;">TOP 50 (50%)</td><td class="num" style="padding:4px 6px;">77.4</td><td class="num" style="padding:4px 6px;">80.2</td><td class="num" style="padding:4px 6px;">83.4</td><td class="num" style="padding:4px 6px;">81.7</td><td class="num" style="padding:4px 6px;background:#fef3c7;">82.1</td></tr>
            </tbody>
          </table>
        </div>

      </div>
      <div class="ins" style="margin-top:14px;"><strong>결론: "50/80 법칙"</strong> &mdash; 상위 20%(20개)가 약 55~63%로 전통적 80/20 불일치. <strong>상위 50개(50%)가 약 80~86%의 매출을 차지</strong>. KR은 TOP5가 33~38%로 집중도 가장 높고, JP는 TOP5 31%&rarr;20%로 하락 추세(메가히트 부재). US는 22년 TOP5 20%&rarr;25년 29%로 <strong>MONOPOLY GO! 등 메가히트 등장으로 집중 심화</strong>.</div>
      <div class="formula-box">
        <strong>&#x1F4D0; 정의/공식</strong><br>
        &bull; 기준: 각 국가 연도별 매출 TOP 100 게임 (in_revenue_top100_unified_os 기준, 연간 합산 순위 100위 이내)<br>
        &bull; 집중도(%) = 상위 N개 게임 매출 합 / TOP 100 전체 매출 합 &times; 100<br>
        &bull; "80/20 법칙": 상위 20%의 고객(또는 제품)이 전체 매출의 80%를 생성한다는 파레토 법칙
      </div>
    </div>
  </div>
'''

def task4_rank_sections(html):
    print("\n=== Task 4: Rank + Concentration sections ===")
    # Check if already present
    if '매출 집중도 분석' in html:
        print("  Already present - skip")
        verify(html, "Task 4 skipped")
        return html
    marker = '  <div class="conclusion kr">'
    pos = html.find(marker)
    if pos == -1:
        raise RuntimeError("conclusion kr marker not found")
    html = html[:pos] + RANK_SECTION + '\n' + html[pos:]
    verify(html, "Task 4 done")
    return html

# =========================================================
# Task 5: Quarterly charts per country + seasonality insights
# =========================================================
QUARTERLY = {
    'KR': [(2022,1,4142),(2022,2,3703),(2022,3,3779),(2022,4,3716),
           (2023,1,4265),(2023,2,3771),(2023,3,4047),(2023,4,3927),
           (2024,1,4469),(2024,2,4359),(2024,3,4595),(2024,4,4528),
           (2025,1,4379),(2025,2,4921),(2025,3,4999),(2025,4,4903),
           (2026,1,4071)],
    'JP': [(2022,1,11460),(2022,2,9083),(2022,3,9269),(2022,4,8987),
           (2023,1,9996),(2023,2,8450),(2023,3,8778),(2023,4,9023),
           (2024,1,9657),(2024,2,8512),(2024,3,9240),(2024,4,9219),
           (2025,1,9596),(2025,2,8984),(2025,3,8907),(2025,4,8745),
           (2026,1,8611)],
    'US': [(2022,1,15120),(2022,2,14277),(2022,3,14347),(2022,4,15006),
           (2023,1,15017),(2023,2,15164),(2023,3,16939),(2023,4,18299),
           (2024,1,20079),(2024,2,19678),(2024,3,18767),(2024,4,18914),
           (2025,1,19919),(2025,2,19556),(2025,3,20663),(2025,4,19857),
           (2026,1,18686)],
}

SEASON = {
    'KR': 'Q3 4,355 &rarr; Q1 4,314 &rarr; Q4 4,269 &rarr; Q2 4,189. 시기별 변화.',
    'JP': 'Q1 압도적. Q1 10,177 &rarr; Q3 9,049 &rarr; Q4 8,994 &rarr; Q2 8,757.',
    'US': 'Q4 홀리데이. Q4 18,019 &rarr; Q3 17,679 &rarr; Q1 17,534 &rarr; Q2 17,169.',
}

def gen_quarterly_chart(country, color, name):
    data = QUARTERLY[country]
    vals = [d[2] for d in data]
    labels = [f"'{d[0]%100}.{d[1]}Q" for d in data]
    pct = [None] + [(vals[i] - vals[i-1]) / vals[i-1] * 100 for i in range(1, len(vals))]
    n = len(data)
    mn, mx = min(vals), max(vals)
    rng = mx - mn if mx != mn else 1
    chart_w, chart_h = 760, 160
    pad_l, pad_r, pad_t, pad_b = 50, 20, 20, 60
    plot_w = chart_w - pad_l - pad_r
    plot_h = chart_h - pad_t - pad_b
    xs = [pad_l + i * plot_w / (n-1) for i in range(n)]
    bar_w = plot_w / n * 0.65
    bars_html = ''
    for i, (x, v) in enumerate(zip(xs, vals)):
        bar_h = (v - mn) / rng * plot_h if rng > 0 else 0
        bar_y = pad_t + plot_h - bar_h
        if i == 0:
            fill = '#94a3b8'
        elif vals[i] > vals[i-1] * 1.03:
            fill = color
        elif vals[i] < vals[i-1] * 0.97:
            fill = '#ef4444'
        else:
            fill = '#cbd5e1'
        bars_html += f'<rect x="{x-bar_w/2:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{fill}" rx="2"/>'
        bars_html += f'<text x="{x:.1f}" y="{bar_y-3:.1f}" text-anchor="middle" font-size="8" fill="#475569" font-weight="600">{v:,}</text>'
        # QoQ label
        p = pct[i]
        if p is not None:
            if p > 3:
                qoq_color, qoq_text = '#059669', f'+{p:.1f}%'
            elif p < -3:
                qoq_color, qoq_text = '#dc2626', f'{p:.1f}%'
            else:
                qoq_color, qoq_text = '#94a3b8', f'{p:+.1f}%'
            bars_html += f'<text x="{x:.1f}" y="{pad_t+plot_h+12:.1f}" text-anchor="middle" font-size="7" fill="{qoq_color}" font-weight="600">{qoq_text}</text>'
        # Quarter label
        is_26 = data[i][0] == 2026
        label_color = '#f59e0b' if is_26 else '#94a3b8'
        font_w = '700' if is_26 else '400'
        bars_html += f'<text x="{x:.1f}" y="{pad_t+plot_h+24:.1f}" text-anchor="middle" font-size="8" fill="{label_color}" font-weight="{font_w}">{labels[i]}</text>'

    y_labels = ''
    for v in [mn, (mn+mx)//2, mx]:
        ratio = (v - mn) / rng if rng > 0 else 0
        y = pad_t + plot_h - ratio * plot_h
        y_labels += f'<text x="{pad_l-5}" y="{y+3:.1f}" text-anchor="end" font-size="7" fill="#94a3b8">{v:,}</text>'
        y_labels += f'<line x1="{pad_l}" y1="{y:.1f}" x2="{chart_w-pad_r}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>'

    season = SEASON[country]
    return f'''
  <!-- 분기별 매출 추이 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num" style="background:{color};">&#x1F4C8;</div>
      <div class="step-info">
        <div class="step-q">{name} 분기별 매출 추이 &mdash; 계절성 패턴</div>
        <div class="step-a">막대: 월평균 매출(억원) &middot; <span style="color:{color};">&#9650;성장(+3%&uarr;)</span> / <span style="color:#ef4444;">&#9660;하락(-3%&darr;)</span> / <span style="color:#94a3b8;">&ndash;보합</span></div>
      </div>
    </div>
    <div class="step-body">
      <svg viewBox="0 0 {chart_w} {chart_h}" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;" preserveAspectRatio="xMidYMid meet">
        {y_labels}
        {bars_html}
      </svg>
      <div class="ins" style="margin-top:10px;"><strong>계절성:</strong> {season}</div>
    </div>
  </div>
'''

def task5_quarterly_charts(html):
    print("\n=== Task 5: Quarterly charts per country ===")
    if '분기별 매출 추이' in html:
        print("  Already present - skip")
        verify(html, "Task 5 skipped")
        return html

    charts = {
        'KR': gen_quarterly_chart('KR', '#3b82f6', '&#127472;&#127479; KR 한국 시장'),
        'JP': gen_quarterly_chart('JP', '#ef4444', '&#127471;&#127477; JP 일본 시장'),
        'US': gen_quarterly_chart('US', '#a855f7', '&#127482;&#127480; US 미국 시장'),
    }

    # Insert before conclusion per country
    # KR: before '  <div class="conclusion kr">'
    # JP: find jp panel, then '</div>\n\n<div class="ctab-panel" id="us">' or conclusion jp
    # Find each panel's closing

    # KR conclusion
    kr_pos = html.find('  <div class="conclusion kr">')
    if kr_pos == -1:
        raise RuntimeError("conclusion kr marker not found")
    html = html[:kr_pos] + charts['KR'] + '\n' + html[kr_pos:]

    # JP: find the jp panel end. The panel ends when <div class="ctab-panel" id="us"> starts
    jp_end = html.find('<div class="ctab-panel" id="us">')
    if jp_end == -1:
        raise RuntimeError("us panel start not found")
    # Find the closing </div> before this that closes jp panel
    # JP panel has no conclusion - just ends. Insert before </div>\n\n<div class="ctab-panel" id="us">
    # Actually look for conclusion jp first
    conclusion_jp = html.rfind('<div class="conclusion jp">', 0, jp_end)
    if conclusion_jp > 0:
        html = html[:conclusion_jp] + charts['JP'] + '\n  ' + html[conclusion_jp:]
    else:
        # insert right before </div>...<div class="ctab-panel" id="us">
        # find the ctab-panel id="us" position and walk backwards for panel close
        # Find the last </div> immediately before us panel start
        # just insert before us panel within jp block - we need jp closing div
        # simpler: find "</div>\n\n<div class=\"ctab-panel\" id=\"us\""
        m = re.search(r'(</div>\s*\n\s*)(<div class="ctab-panel" id="us">)', html)
        if m:
            html = html[:m.start(1)] + charts['JP'] + '\n' + html[m.start(1):]
        else:
            raise RuntimeError("Could not find jp panel end")

    # US: similar - find US panel end
    # US panel is the last. Find conclusion us
    conclusion_us = html.rfind('<div class="conclusion us">')
    if conclusion_us > 0:
        html = html[:conclusion_us] + charts['US'] + '\n  ' + html[conclusion_us:]
    else:
        # Find us panel closing (before </div> that closes tab-country-deep)
        # Search for pattern: end of us panel - find last instance
        us_start = html.find('<div class="ctab-panel" id="us">')
        # Find matching closing div - walk through from us_start
        # For simplicity, find the next "</div>\n</div>" which closes ctab-panel + its parent?
        # We'll find the pattern \n</div>\n</div>\n</div> that closes tab-country-deep
        # Insert before that
        tail_m = re.search(r'</div>\s*\n\s*</div>\s*\n\s*</div>\s*\n\s*<!-- ===== JavaScript', html[us_start:])
        if tail_m:
            insert_pos = us_start + tail_m.start()
            # Walk back to find last child boundary
            html = html[:insert_pos] + charts['US'] + '\n' + html[insert_pos:]
        else:
            # Fallback: insert before JavaScript block
            js_pos = html.find('<!-- ===== JavaScript =====')
            # find last </div> </div> </div> before js
            pre = html[:js_pos]
            last_ctab_us = pre.rfind('<div class="ctab-panel" id="us">')
            # insert near end of us panel - find last </div> before </div></div>
            # simpler: insert just before the last </div> immediately preceding JavaScript section
            # find last "</div>" before js_pos
            # We want to insert inside us panel, so find 3rd-to-last </div> before js
            close_positions = [m.start() for m in re.finditer(r'</div>', pre)]
            if len(close_positions) >= 3:
                # 3rd from last - closes us panel
                insert_pos = close_positions[-3]
                html = html[:insert_pos] + charts['US'] + '\n' + html[insert_pos:]

    verify(html, "Task 5 done")
    return html

# =========================================================
# Task 6: CN share chart in ALL panel (between Step 2 and Step 3)
# =========================================================
CN_SHARE = {
    'KR': [(2022,21.8),(2023,25.5),(2024,35.8),(2025,37.0),(2026,37.7)],
    'JP': [(2022,25.9),(2023,26.7),(2024,32.1),(2025,32.6),(2026,34.8)],
    'US': [(2022,15.5),(2023,13.8),(2024,15.4),(2025,22.3),(2026,26.8)],
}

def gen_cn_share_chart():
    """Horizontal bar chart: years top-to-bottom, 3 horizontal bars per year (KR/JP/US)."""
    years = [2022, 2023, 2024, 2025, 2026]
    countries = [('KR', '#3b82f6'), ('JP', '#ef4444'), ('US', '#a855f7')]

    chart_w = 820
    row_h = 40  # per year
    pad_t, pad_b = 30, 20
    pad_l = 60  # for year label
    pad_r = 20
    chart_h = pad_t + len(years) * row_h + pad_b
    plot_w = chart_w - pad_l - pad_r

    max_pct = 40
    bars_html = ''

    for yi, year in enumerate(years):
        row_y = pad_t + yi * row_h
        # Row background for 2026
        if year == 2026:
            bars_html += f'<rect x="{pad_l-50}" y="{row_y-4}" width="{chart_w-pad_l+50}" height="{row_h}" fill="#fef3c7" opacity="0.5"/>'
        # Year label
        fw = '700' if year == 2026 else '600'
        yc = '#b45309' if year == 2026 else '#475569'
        bars_html += f'<text x="{pad_l-10}" y="{row_y+row_h/2+4:.1f}" text-anchor="end" font-size="11" fill="{yc}" font-weight="{fw}">{year}</text>'

        # 3 bars for KR/JP/US
        bar_h = (row_h - 8) / 3
        for ci, (country, color) in enumerate(countries):
            pct = next(p for (y, p) in CN_SHARE[country] if y == year)
            bar_y = row_y + 2 + ci * bar_h
            bar_w = pct / max_pct * plot_w
            bars_html += f'<rect x="{pad_l}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h-1:.1f}" fill="{color}" rx="2"/>'
            # Value at end of bar
            bars_html += f'<text x="{pad_l+bar_w+4:.1f}" y="{bar_y+bar_h/2+3:.1f}" font-size="9" fill="{color}" font-weight="700">{country} {pct}%</text>'

    # X axis ticks
    for v in [0, 10, 20, 30, 40]:
        x = pad_l + v / max_pct * plot_w
        bars_html += f'<line x1="{x:.1f}" y1="{pad_t-5}" x2="{x:.1f}" y2="{chart_h-pad_b}" stroke="#e2e8f0" stroke-dasharray="2,2"/>'
        bars_html += f'<text x="{x:.1f}" y="{pad_t-8}" text-anchor="middle" font-size="8" fill="#94a3b8">{v}%</text>'

    return f'''
  <!-- 중화권 퍼블리셔 비중 추이 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num" style="background:#d97706;">&#x1F1E8;&#x1F1F3;</div>
      <div class="step-info">
        <div class="step-q">3국 중화권 퍼블리셔 매출 비중 추이 (연도별, %)</div>
        <div class="step-a">KR <span style="color:#3b82f6;font-weight:700;">21.8% &rarr; 37.7%</span> &middot; JP <span style="color:#ef4444;font-weight:700;">25.9% &rarr; 34.8%</span> &middot; US <span style="color:#a855f7;font-weight:700;">15.5% &rarr; 26.8%</span> &mdash; 3국 모두 중화권 침투 가속</div>
      </div>
    </div>
    <div class="step-body">
      <svg viewBox="0 0 {chart_w} {chart_h}" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;" preserveAspectRatio="xMidYMid meet">
        {bars_html}
      </svg>
      <div class="ins" style="margin-top:10px;"><strong>핵심:</strong> KR이 가장 빠르게 중화권화 (+15.9%p). US는 25년부터 본격 진입 (+11.3%p). JP는 가장 안정적 성장 (+8.9%p). <strong>"중화권 침투는 시장 무관 일관된 트렌드"</strong>.</div>
    </div>
  </div>
'''

def task6_cn_chart(html):
    print("\n=== Task 6: CN share chart in ALL panel ===")
    if '3국 중화권 퍼블리셔 매출 비중 추이' in html:
        print("  Already present - skip")
        verify(html, "Task 6 skipped")
        return html
    cn_chart = gen_cn_share_chart()

    # ALL panel steps at lines 2230, 2294, 2321
    # We want to insert between Step 2 (starts at 2294) and Step 3 (starts at 2321)
    # Find all panel
    all_start = html.find('<div class="ctab-panel active" id="all">')
    if all_start == -1:
        raise RuntimeError("ALL panel not found")

    # Find the 3rd <div class="step"> in all panel (step 3)
    # Actually: Step 3 in ALL panel is "장르별 월평균 매출 변화"
    step3_pos = html.find('장르별 월평균 매출 변화', all_start)
    if step3_pos == -1:
        raise RuntimeError("All panel step 3 not found")

    # Walk back to find the step div opening before step3_pos
    step_open = html.rfind('  <div class="step">', all_start, step3_pos)
    if step_open == -1:
        raise RuntimeError("Step 3 div open not found")

    html = html[:step_open] + cn_chart + '\n' + html[step_open:]
    verify(html, "Task 6 done")
    return html

# =========================================================
# Task 7: Renumber tabs and update CSS
# =========================================================
def task7_renumber(html):
    print("\n=== Task 7: Renumber tabs and colors ===")

    # Current buttons after task 1: country-deep(badge 1), criteria(badge 3)
    # Need: country-deep(1), growth(2), criteria(3)
    # Check current state
    # After task 1, tab-analysis button should be removed.

    # Need to add tab-growth button after country-deep button, before criteria
    # Current structure:
    #   <button class="tab-btn active" data-tab="tab-country-deep">...badge 1...</button>
    #   <button class="tab-btn" data-tab="tab-criteria">...badge 3...</button>

    if 'data-tab="tab-growth"' in html:
        # Button already there? Check
        if html.count('data-tab="tab-growth"') >= 1:
            print("  tab-growth button already present")

    # Remove any existing tab-growth button first (to avoid dups)
    html = re.sub(
        r'\s*<button class="tab-btn" data-tab="tab-growth"[^>]*>\s*<span class="tab-badge">\d+</span>[^<]*</button>\s*\n',
        '\n  ',
        html
    )

    # Insert tab-growth button before criteria button
    criteria_btn_pattern = r'(<button class="tab-btn" data-tab="tab-criteria"[^>]*>\s*<span class="tab-badge">)\d+(</span>[^<]*</button>)'
    growth_btn = '<button class="tab-btn" data-tab="tab-growth" onclick="switchTab(\'tab-growth\')">\n    <span class="tab-badge">2</span> 25년 성장 게임 (광고/연령)\n  </button>\n  '

    html = re.sub(
        criteria_btn_pattern,
        growth_btn + r'\g<1>3\g<2>',
        html,
        count=1
    )

    # Ensure country-deep badge is 1
    html = re.sub(
        r'(<button class="tab-btn active" data-tab="tab-country-deep"[^>]*>\s*<span class="tab-badge">)\d+(</span>)',
        r'\g<1>1\g<2>',
        html,
        count=1
    )

    # Add CSS rule for tab-growth badge (if not present)
    if '.tab-btn[data-tab="tab-growth"]' not in html:
        # Add after criteria CSS rule
        html = html.replace(
            '.tab-btn[data-tab="tab-criteria"] .tab-badge { background: #475569; }',
            '.tab-btn[data-tab="tab-criteria"] .tab-badge { background: #475569; }\n  .tab-btn[data-tab="tab-growth"] .tab-badge { background: #1e293b; }',
            1
        )

    verify(html, "Task 7 done")
    return html

# =========================================================
# MAIN
# =========================================================
def main():
    # Backup
    backup = MAIN + '.bak.' + time.strftime('%Y%m%d_%H%M%S')
    shutil.copy(MAIN, backup)
    print(f"Backup: {backup}")

    html = read_html()
    verify(html, "initial")
    print(f"Initial size: {len(html):,}")

    html = task1_extract_ag(html)
    html = task3_dart_inline(html)
    html = task4_rank_sections(html)
    html = task5_quarterly_charts(html)
    html = task6_cn_chart(html)
    html = task7_renumber(html)

    verify(html, "FINAL")
    write_html(html)
    print(f"\nFinal size: {len(html):,} bytes")
    print("All tasks applied successfully.")

if __name__ == '__main__':
    main()
