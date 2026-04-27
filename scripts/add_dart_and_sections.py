#!/usr/bin/env python3
"""Add DART operating income column to Step star table + new sections"""
import re

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# DART operating income by publisher (연결, 억원)
DART = {
    '엔씨소프트':    {2022:5590, 2023:1373, 2024:-1092, 2025:161},
    '넥슨':          None,  # JP listed
    '넷마블':        {2022:-1087, 2023:-685, 2024:2156, 2025:3525},
    '카카오게임즈':  {2022:1758, 2023:745, 2024:191, 2025:-396},
    'NHN':           {2022:391, 2023:556, 2024:-326, 2025:1324},
    '컴투스':        {2022:-167, 2023:-332, 2024:61, 2025:26},
    '위메이드':      {2022:-849, 2023:-1104, 2024:71, 2025:107},
    '111%':          None,
    'DRIMAGE':       None,
    '데브시스터즈':  {2022:-199, 2023:-480, 2024:272, 2025:64},
    '크래프톤':      {2022:7516, 2023:7680, 2024:11825, 2025:10544},
    '네오위즈':      {2022:196, 2023:316, 2024:329, 2025:600},
    'EPIDGames':     None,
    '스마일게이트':  None,
    '웹젠':          {2022:830, 2023:499, 2024:546, 2025:297},
    'NTRANCE Corp':  None,
    'Supermagic':    None,
    'Project Moon':  None,
    'AWESOMEPIECE':  None,
    'STUDIOBSIDE':   None,
    'Zempot':        None,
    '스마트나우':    None,
    '빌리언게임즈':  None,
    'STUDIO LICO Corp.': None,
    'ESTgames Corp.': None,
    'Stand Egg':     None,
    '그라비티':      None,
    'PlaywithKorea Inc.': None,
    'VFive Games Co.,Ltd.': None,
    'Gameduo':       None,
    'LIONHEART STUDIO': None,
    'mobirix':       None,
    'NEW NORMAL SOFT': None,
    '펄어비스':      {2022:164, 2023:-164, 2024:-123, 2025:-148},
}

def fmt_dart(d):
    """Format DART OP column: '25 value with trend"""
    if d is None:
        return '<td class="num" style="background:#f8fafc;color:#cbd5e1;font-size:0.68rem;">-</td>'
    vals = []
    for yr in [2022, 2023, 2024, 2025]:
        v = d.get(yr)
        if v is not None:
            if v >= 0:
                vals.append(f"<span style='color:#059669;'>{v:,}</span>")
            else:
                vals.append(f"<span style='color:#dc2626;'>{v:,}</span>")
        else:
            vals.append("-")
    # Show as: 22/23/24/25
    return f'<td class="num" style="background:#f0f0ff;font-size:0.62rem;line-height:1.4;white-space:nowrap;">' + \
           f"<span style='color:#94a3b8;'>22:</span>{vals[0]}<br>" + \
           f"<span style='color:#94a3b8;'>23:</span>{vals[1]}<br>" + \
           f"<span style='color:#94a3b8;'>24:</span>{vals[2]}<br>" + \
           f"<span style='color:#94a3b8;font-weight:700;'>25:</span>{vals[3]}</td>"

def add_dart_column(html):
    """Add DART column to each publisher row in Step star table"""
    # Match publisher rows: <tr style="background:#f0f9ff;"><td><strong>NAME</strong></td>...
    # and description rows: <tr><td colspan="7"...

    # Update colspan from 7 to 8 for description rows in the Step star section
    # Find the Step star section
    star_start = html.find('한국 퍼블리셔 월평균 매출 &amp; 대표 게임')
    if star_start == -1:
        star_start = html.find('한국 퍼블리셔 월평균 매출 & 대표 게임')

    star_end = html.find('</div>\n    </div>\n  </div>\n\n  <div class="conclusion kr">')
    if star_end == -1:
        star_end = html.find('<div class="conclusion kr">')

    if star_start == -1 or star_end == -1:
        print(f"WARN: Could not find Step star section bounds (start={star_start}, end={star_end})")
        return html

    section = html[star_start:star_end]

    # Replace colspan="7" with colspan="8" in this section
    section = section.replace('colspan="7"', 'colspan="8"')

    # Add DART cell to each publisher data row
    for pub_name, dart_data in DART.items():
        dart_cell = fmt_dart(dart_data)
        # Find the row ending pattern for this publisher
        # Pattern: publisher name followed by data cells ending with </td></tr>
        # We need to insert the DART cell before </tr>

        search = f'<strong>{pub_name}</strong>'
        pos = section.find(search)
        if pos == -1:
            continue

        # Find the </tr> after this position (the data row, not description row)
        tr_end = section.find('</tr>', pos)
        if tr_end == -1:
            continue

        # Insert DART cell before </tr>
        section = section[:tr_end] + dart_cell + section[tr_end:]

    # Also handle the totals row
    tot_search = 'TOP 22 합계'
    tot_pos = section.find(tot_search)
    if tot_pos == -1:
        tot_search = 'TOP'
        tot_pos = section.find('class="tot"', section.rfind('<tr'))

    # Find last tot row and add empty DART cell
    last_tot = section.rfind('class="tot"')
    if last_tot != -1:
        tr_end = section.find('</tr>', last_tot)
        if tr_end != -1:
            section = section[:tr_end] + '<td class="num" style="background:#f0f0ff;">-</td>' + section[tr_end:]

    html = html[:star_start] + section + html[star_end:]
    return html

# ============================================================
# NEW SECTIONS HTML
# ============================================================

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

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add DART column to Step star table
    html = add_dart_column(html)
    print("DART column added to Step star table")

    # 2. Insert new sections before conclusion kr
    marker = '  <div class="conclusion kr">'
    pos = html.find(marker)
    if pos != -1:
        html = html[:pos] + RANK_SECTION + '\n' + html[pos:]
        print("Rank + Concentration sections inserted")
    else:
        print("WARN: Could not find conclusion kr marker")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("Done!")

if __name__ == '__main__':
    main()
