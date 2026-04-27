#!/usr/bin/env python3
"""
4가지 수정 일괄 처리:
1. 뱀피르 MMORPG로 통일 (KR MMORPG/비MMORPG 값 재계산)
2. JP/US Step 3 RPG 통합 (MMORPG/비MMORPG 분리 해제)
3. 각 국가 패널에 분기별 매출 추이 차트 추가
4. ALL 패널 Step 2 다음에 중화권 비중 추이 차트 추가
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# ============================================================
# DATA
# ============================================================

# 분기별 매출 (월평균 억원)
QUARTERLY = {
    'KR': [
        (2022,1,4142),(2022,2,3703),(2022,3,3779),(2022,4,3716),
        (2023,1,4265),(2023,2,3771),(2023,3,4047),(2023,4,3927),
        (2024,1,4469),(2024,2,4359),(2024,3,4595),(2024,4,4528),
        (2025,1,4379),(2025,2,4921),(2025,3,4957),(2025,4,4870),
        (2026,1,4063),
    ],
    'JP': [
        (2022,1,11460),(2022,2,9083),(2022,3,9269),(2022,4,8987),
        (2023,1,9996),(2023,2,8450),(2023,3,8778),(2023,4,9023),
        (2024,1,9657),(2024,2,8512),(2024,3,9240),(2024,4,9219),
        (2025,1,9596),(2025,2,8984),(2025,3,8907),(2025,4,8745),
        (2026,1,8611),
    ],
    'US': [
        (2022,1,15120),(2022,2,14277),(2022,3,14347),(2022,4,15006),
        (2023,1,15017),(2023,2,15164),(2023,3,16939),(2023,4,18299),
        (2024,1,20079),(2024,2,19678),(2024,3,18767),(2024,4,18914),
        (2025,1,19919),(2025,2,19556),(2025,3,20663),(2025,4,19857),
        (2026,1,18686),
    ],
}

# 중화권 비중 추이
CN_SHARE = {
    'KR': [(2022,21.8,837),(2023,25.5,1019),(2024,35.8,1605),(2025,37.0,1770),(2026,37.7,1533)],
    'JP': [(2022,25.9,2511),(2023,26.7,2421),(2024,32.1,2938),(2025,32.6,2954),(2026,34.8,3001)],
    'US': [(2022,15.5,2281),(2023,13.8,2249),(2024,15.4,2972),(2025,22.3,4458),(2026,26.8,5010)],
}

# ============================================================
# FUNCTIONS
# ============================================================

def gen_quarterly_chart(country, color, name):
    """분기별 매출 차트 SVG + 표"""
    data = QUARTERLY[country]
    vals = [d[2] for d in data]
    labels = [f"'{d[0]%100}.{d[1]}Q" for d in data]

    # 성수기/불경기 판단: 직전분기 대비
    deltas = [None] + [vals[i] - vals[i-1] for i in range(1, len(vals))]
    pct = [None] + [(vals[i] - vals[i-1]) / vals[i-1] * 100 for i in range(1, len(vals))]

    # SVG 좌표 계산
    n = len(data)
    mn, mx = min(vals), max(vals)
    rng = mx - mn if mx != mn else 1
    chart_w = 760
    chart_h = 120
    pad_l, pad_r, pad_t, pad_b = 50, 20, 20, 30
    plot_w = chart_w - pad_l - pad_r
    plot_h = chart_h - pad_t - pad_b

    xs = [pad_l + i * plot_w / (n-1) for i in range(n)]
    ys = [pad_t + plot_h - (v - mn) / rng * plot_h for v in vals]

    # Bar chart bars
    bar_w = plot_w / n * 0.65
    bars_html = ''
    for i, (x, y, v) in enumerate(zip(xs, ys, vals)):
        bar_h = (v - mn) / rng * plot_h if rng > 0 else 0
        bar_y = pad_t + plot_h - bar_h
        # 색상: 직전분기 대비 상승=녹색, 하락=붉은색
        if i == 0:
            fill = '#94a3b8'
        elif vals[i] > vals[i-1] * 1.03:
            fill = color
        elif vals[i] < vals[i-1] * 0.97:
            fill = '#ef4444'
        else:
            fill = '#cbd5e1'
        bars_html += f'<rect x="{x-bar_w/2:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{fill}" rx="2"/>'
        # Value label
        bars_html += f'<text x="{x:.1f}" y="{bar_y-3:.1f}" text-anchor="middle" font-size="8" fill="#475569" font-weight="600">{v:,}</text>'
        # Quarter label
        is_26 = data[i][0] == 2026
        label_color = '#f59e0b' if is_26 else '#94a3b8'
        font_w = '700' if is_26 else '400'
        bars_html += f'<text x="{x:.1f}" y="{chart_w-440:.1f}" text-anchor="middle" font-size="8" fill="{label_color}" font-weight="{font_w}">{labels[i]}</text>'

    # Y axis labels (3 levels)
    y_labels = ''
    for v in [mn, (mn+mx)//2, mx]:
        ratio = (v - mn) / rng if rng > 0 else 0
        y = pad_t + plot_h - ratio * plot_h
        y_labels += f'<text x="{pad_l-5}" y="{y+3:.1f}" text-anchor="end" font-size="7" fill="#94a3b8">{v:,}</text>'
        y_labels += f'<line x1="{pad_l}" y1="{y:.1f}" x2="{chart_w-pad_r}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>'

    # 표: 분기별 변화율
    table_rows = ''
    for i, ((yr, q, v), p) in enumerate(zip(data, pct)):
        if p is None:
            cls, txt = '', '-'
        elif p > 3:
            cls, txt = 'up', f'+{p:.1f}%'
        elif p < -3:
            cls, txt = 'dn', f'{p:.1f}%'
        else:
            cls, txt = '', f'{p:+.1f}%'
        col26 = ' col26' if yr == 2026 else ''
        table_rows += f'<td class="num{col26} {cls}" style="padding:3px 4px;font-size:0.65rem;">{txt}</td>'

    head_q = ''
    for yr, q, v in data:
        col26 = ' col26' if yr == 2026 else ''
        head_q += f'<th class="num{col26}" style="padding:3px 4px;font-size:0.62rem;color:#64748b;">{yr%100}Q{q}</th>'

    return f'''
  <!-- 분기별 매출 추이 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num" style="background:{color};">📈</div>
      <div class="step-info">
        <div class="step-q">{name} 분기별 매출 추이 — 성수기/불경기 패턴</div>
        <div class="step-a">막대: 월평균 매출 (억원) · 색상: 직전분기 대비 <span style="color:{color};">▲성장(+3%↑)</span> / <span style="color:#ef4444;">▼하락(-3%↓)</span> / <span style="color:#94a3b8;">─보합</span></div>
      </div>
    </div>
    <div class="step-body">
      <svg viewBox="0 0 {chart_w} {chart_h}" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;" preserveAspectRatio="xMidYMid meet">
        {y_labels}
        {bars_html}
      </svg>
      <table style="margin-top:8px;width:100%;font-size:0.7rem;border-collapse:collapse;">
        <thead><tr><th style="text-align:left;padding:3px 4px;font-size:0.62rem;color:#64748b;">QoQ 변화율</th>{head_q}</tr></thead>
        <tbody><tr><td style="padding:3px 4px;font-size:0.62rem;color:#64748b;">전분기 대비</td>{table_rows}</tr></tbody>
      </table>
    </div>
  </div>
'''

def gen_cn_share_chart():
    """3국 중화권 비중 추이 차트"""
    chart_w = 800
    chart_h = 200
    pad_l, pad_r, pad_t, pad_b = 50, 20, 30, 40
    plot_w = chart_w - pad_l - pad_r
    plot_h = chart_h - pad_t - pad_b

    years = [2022, 2023, 2024, 2025, 2026]
    n_yrs = len(years)
    n_countries = 3

    # 그룹 너비 / 막대 너비
    group_w = plot_w / n_yrs
    bar_w = group_w / (n_countries + 1)

    countries = [('KR','#3b82f6'), ('JP','#ef4444'), ('US','#a855f7')]

    # Y axis: 0~40%
    max_pct = 40
    y_labels = ''
    for v in [0, 10, 20, 30, 40]:
        y = pad_t + plot_h - v / max_pct * plot_h
        y_labels += f'<text x="{pad_l-5}" y="{y+3:.1f}" text-anchor="end" font-size="8" fill="#94a3b8">{v}%</text>'
        y_labels += f'<line x1="{pad_l}" y1="{y:.1f}" x2="{chart_w-pad_r}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>'

    # Bars
    bars_html = ''
    for yi, year in enumerate(years):
        group_x = pad_l + yi * group_w + group_w / 2
        # Year label
        is_26 = year == 2026
        label_color = '#f59e0b' if is_26 else '#94a3b8'
        font_w = '700' if is_26 else '400'
        bars_html += f'<text x="{group_x:.1f}" y="{chart_h-pad_b+15}" text-anchor="middle" font-size="9" fill="{label_color}" font-weight="{font_w}">{year}</text>'

        for ci, (country, color) in enumerate(countries):
            data_row = next((d for d in CN_SHARE[country] if d[0] == year), None)
            if not data_row:
                continue
            yr, pct, rev = data_row
            x = group_x + (ci - 1) * bar_w
            bar_h = pct / max_pct * plot_h
            bar_y = pad_t + plot_h - bar_h
            bars_html += f'<rect x="{x-bar_w/2+1:.1f}" y="{bar_y:.1f}" width="{bar_w-2:.1f}" height="{bar_h:.1f}" fill="{color}" rx="1"/>'
            # Value
            bars_html += f'<text x="{x:.1f}" y="{bar_y-3:.1f}" text-anchor="middle" font-size="8" fill="{color}" font-weight="700">{pct}</text>'

    # Legend
    legend_html = ''
    for ci, (country, color) in enumerate(countries):
        x = chart_w - 200 + ci * 65
        legend_html += f'<rect x="{x}" y="{pad_t-25}" width="10" height="10" fill="{color}" rx="2"/>'
        flag = {'KR':'🇰🇷 KR','JP':'🇯🇵 JP','US':'🇺🇸 US'}[country]
        legend_html += f'<text x="{x+14}" y="{pad_t-17}" font-size="9" fill="#475569" font-weight="600">{flag}</text>'

    # Table
    table_rows = ''
    for yi, year in enumerate(years):
        col26 = ' col26' if year == 2026 else ''
        cells = f'<td class="num{col26}" style="padding:4px 8px;">{year}</td>'
        for country, _ in countries:
            data_row = next((d for d in CN_SHARE[country] if d[0] == year), None)
            if data_row:
                cells += f'<td class="num{col26}" style="padding:4px 8px;">{data_row[1]}%</td>'
                cells += f'<td class="num{col26}" style="padding:4px 8px;color:#64748b;">{data_row[2]:,}억</td>'
            else:
                cells += '<td>-</td><td>-</td>'
        table_rows += f'<tr>{cells}</tr>'

    return f'''
  <!-- 중화권 퍼블리셔 비중 추이 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num" style="background:#d97706;">🇨🇳</div>
      <div class="step-info">
        <div class="step-q">3국 중화권 퍼블리셔 매출 비중 추이 (연도별, %)</div>
        <div class="step-a">KR <span style="color:#3b82f6;font-weight:700;">21.8% → 37.7%</span> · JP <span style="color:#ef4444;font-weight:700;">25.9% → 34.8%</span> · US <span style="color:#a855f7;font-weight:700;">15.5% → 26.8%</span> — 3국 모두 중화권 침투 가속</div>
      </div>
    </div>
    <div class="step-body">
      <svg viewBox="0 0 {chart_w} {chart_h}" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;" preserveAspectRatio="xMidYMid meet">
        {legend_html}
        {y_labels}
        {bars_html}
      </svg>
      <table style="margin-top:12px;width:100%;font-size:0.74rem;border-collapse:collapse;">
        <thead>
          <tr style="background:#f1f5f9;">
            <th style="padding:6px 8px;text-align:left;color:#475569;">연도</th>
            <th class="num" style="padding:6px 8px;color:#3b82f6;">KR 비중</th>
            <th class="num" style="padding:6px 8px;color:#94a3b8;">KR 매출</th>
            <th class="num" style="padding:6px 8px;color:#ef4444;">JP 비중</th>
            <th class="num" style="padding:6px 8px;color:#94a3b8;">JP 매출</th>
            <th class="num" style="padding:6px 8px;color:#a855f7;">US 비중</th>
            <th class="num" style="padding:6px 8px;color:#94a3b8;">US 매출</th>
          </tr>
        </thead>
        <tbody>{table_rows}</tbody>
      </table>
      <div class="ins" style="margin-top:10px;">
        <strong>핵심:</strong> KR이 가장 빠르게 중화권화 (+15.9%p), 22년 21.8% → 26년 37.7%. US는 25년부터 본격 진입 (+11.3%p). JP는 가장 안정적 성장 (+8.9%p). <strong>"중화권 침투는 시장 무관 일관된 트렌드"</strong>.
      </div>
    </div>
  </div>
'''

# ============================================================
# MAIN
# ============================================================

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # ===== #1: KR MMORPG / 비MMORPG 값 갱신 (뱀피르 정확 반영) =====
    # 신규: MMORPG 1957/1890/1495/1466/679, 비MMORPG 614/646/725/752/945
    # 25년 전후: MMORPG pre=avg(1957,1890,1495)=1781, post=(1466*12+679*3)/15=1308
    #           비MMORPG pre=avg(614,646,725)=662, post=(752*12+945*3)/15=791

    kr_mmo_old_pattern = re.compile(r'MMORPG</td><td class="num">1,957</td><td class="num">1,890</td><td class="num">1,495</td><td class="num">1,340</td><td class="num col26 dn">643</td>')
    if kr_mmo_old_pattern.search(html):
        # MMORPG row update
        html = re.sub(
            r'(MMORPG</td><td class="num">)1,957(</td><td class="num">)1,890(</td><td class="num">)1,495(</td><td class="num)( dn">)1,340(</td><td class="num col26 dn">)643',
            r'\g<1>1,957\g<2>1,890\g<3>1,495\g<4> up">1,466\g<6>679',
            html, count=1
        )
        print("KR MMORPG row updated")
    else:
        # Try without dn class
        html = re.sub(
            r'(>MMORPG</td><td class="num">1,957</td><td class="num">1,890</td><td class="num">1,495</td><td class="num[^"]*">)1,340(</td><td class="num col26[^"]*">)643',
            r'\g<1>1,466\g<2>679',
            html, count=1
        )
        print("KR MMORPG (alt) updated")

    # 비MMORPG row update: 614/646/725/878/981 → 614/646/725/752/945
    html = re.sub(
        r'(비MMORPG[^<]*</td><td class="num">614</td><td class="num">646</td><td class="num">725</td><td class="num[^"]*">)878(</td><td class="num col26[^"]*">)981',
        r'\g<1>752\g<2>945',
        html, count=1
    )
    print("KR 비MMORPG row updated")

    # KR MMORPG 25년 전후 변화: pre 1781 → post 1308 = -473억 (-27%)
    # 기존 텍스트 패턴: <strong>1,781 → 1,200</strong><br>-580억 등
    html = html.replace('1,781 → 1,200', '1,781 → 1,308')
    html = html.replace('-580억 (-33%)', '-473억 (-27%)')

    # KR 비MMORPG 25년 전후: pre 662 → post 791 = +129억 (+19%)
    html = html.replace('662 → 858', '662 → 791')
    html = html.replace('+196억 (+30%)', '+129억 (+19%)')
    html = html.replace('+237B (+36%)', '+129억 (+19%)')

    # ===== #2: JP/US Step 3 RPG 통합 =====
    # JP: MMORPG 행 + 비MMORPG RPG 행 → Role Playing 1행
    # JP Role Playing: 3478/3332/2975/2435/2052
    # JP에서 MMORPG (166/91/54/61/19)와 Non-MMORPG RPG (3312/3241/2948/2374/2046) 행을 찾아 1행으로 합침

    # MMORPG 행 제거 + Non-MMORPG → Role Playing으로 변경
    # JP는 패널에 두 행이 따로 있을 것

    # JP MMORPG 행 제거
    jp_mmo_pattern = r'<tr>\s*<td>(?:<strong>)?MMORPG(?:</strong>)?</td>\s*<td class="num">166</td>.*?</tr>\s*'
    jp_match = re.search(jp_mmo_pattern, html, re.DOTALL)
    if jp_match:
        html = html[:jp_match.start()] + html[jp_match.end():]
        print("JP MMORPG row removed")

    # JP Non-MMORPG RPG 행 → Role Playing으로 통합 (값 업데이트)
    # 현재 비MMORPG 값: 3312/3241/2948/2374/2046 → 통합 3478/3332/2975/2435/2052
    html = re.sub(
        r'(비MMORPG RPG[^<]*</td>\s*<td class="num">)3,312(</td><td class="num[^"]*">)3,241(</td><td class="num[^"]*">)2,948(</td><td class="num[^"]*">)2,374(</td><td class="num col26[^"]*">)2,046',
        r'Role Playing</td>\n          <td class="num">3,478\g<2>3,332\g<3>2,975\g<4>2,435\g<5>2,052',
        html, count=1
    )
    # alternate without 비MMORPG label
    html = re.sub(
        r'(>비MMORPG RPG<)',
        r'>Role Playing<',
        html
    )
    print("JP RPG unified")

    # US: MMORPG 행 (52/0/0/0/0) 제거 + Non-MMORPG (1516/1260/1045/991/717) → Role Playing
    us_mmo_pattern = r'<tr>\s*<td>(?:<strong>)?MMORPG(?:</strong>)?</td>\s*<td class="num">52</td>.*?</tr>\s*'
    us_match = re.search(us_mmo_pattern, html, re.DOTALL)
    if us_match:
        html = html[:us_match.start()] + html[us_match.end():]
        print("US MMORPG row removed")

    # US Non-MMORPG → Role Playing 라벨 변경
    # 데이터: 1516/1260/1045/991/717 → 통합 1520/1260/1045/991/717
    html = re.sub(
        r'(Non-MMORPG RPG[^<]*</td>)',
        r'Role Playing</td>',
        html
    )
    html = re.sub(
        r'(Role Playing</td>\s*<td class="num">)1,516',
        r'\g<1>1,520',
        html
    )
    print("US RPG unified")

    # ===== #3: 분기별 매출 추이 차트 - 각 국가 패널의 헤드라인 다음에 삽입 =====
    # 패턴: 각 국가의 <div class="ctab-panel" id="kr/jp/us">...<div class="headline ...">...</div> 직후

    for country, color, name in [('KR','#3b82f6','🇰🇷 KR 한국 시장'), ('JP','#ef4444','🇯🇵 JP 일본 시장'), ('US','#a855f7','🇺🇸 US 미국 시장')]:
        chart_html = gen_quarterly_chart(country, color, name)
        # Find headline closing for this panel
        # Pattern: id="kr"...<div class="headline kr">...</div>
        panel_id = country.lower()

        # Find the position after the headline div closes
        panel_start = html.find(f'id="{panel_id}"')
        if panel_start == -1:
            print(f"  SKIP {country}: panel not found")
            continue

        # Find headline div within this panel
        headline_start = html.find(f'class="headline {panel_id}"', panel_start)
        if headline_start == -1:
            # Try without panel id
            headline_start = html.find('class="headline', panel_start)
        if headline_start == -1:
            print(f"  SKIP {country}: headline not found")
            continue

        # Find the closing </div> of headline (it has h2 + p inside)
        # Pattern: </p>\n  </div>
        p_close = html.find('</p>', headline_start)
        if p_close == -1:
            continue
        div_close = html.find('</div>', p_close)
        if div_close == -1:
            continue
        insert_pos = div_close + 6  # after </div>

        html = html[:insert_pos] + '\n' + chart_html + html[insert_pos:]
        print(f"  Quarterly chart added to {country}")

    # ===== #4: ALL 패널 Step 2 다음에 중화권 비중 추이 차트 추가 =====
    cn_chart = gen_cn_share_chart()

    # ALL 패널 내 Step 3 (장르별) 직전에 삽입
    # 패턴: ALL 패널의 Step 3 시작 직전
    all_start = html.find('id="all"')
    # Step 3 marker in ALL panel
    step3_pattern = '<!-- Step 3: 장르별'
    step3_pos = html.find(step3_pattern, all_start)
    if step3_pos == -1:
        # Try alternative
        step3_pos = html.find('장르별 월평균 매출 변화', all_start)
        if step3_pos > 0:
            # Find the <div class="step"> before this
            step3_pos = html.rfind('<!-- Step', all_start, step3_pos)

    if step3_pos > 0:
        html = html[:step3_pos] + cn_chart + '\n  ' + html[step3_pos:]
        print("CN share chart added to ALL panel")
    else:
        print("WARN: Could not find Step 3 in ALL panel for CN chart insertion")

    # Verify
    d = html.count('<div')
    c = html.count('</div>')
    print(f'\nFinal div: {d}/{c} diff={d-c}')

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print('Done!')

if __name__ == '__main__':
    main()
