# -*- coding: utf-8 -*-
"""
Step 4 하단 demographics 블록 재구성:
- 연령: 7게임 × 5연도 라인 차트
- 남녀 비중: 7게임 × 26.1Q 기준 수평 누적 막대
- MAU: 테이블 + 합계 행
- DL: 테이블 + 합계 행
"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\webboard_7games.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
GAMES = ['한게임 포커','한게임 섯다&맞고','한게임포커 클래식','한게임 신맞고',
         'Pmang Poker','피망 뉴맞고','WPL (윈조이 포커 리그)']
COLORS = {'한게임 포커':'#0085ca','한게임 섯다&맞고':'#10b981','한게임포커 클래식':'#8b5cf6',
          '한게임 신맞고':'#f59e0b','Pmang Poker':'#dc2626','피망 뉴맞고':'#ec4899',
          'WPL (윈조이 포커 리그)':'#64748b'}

def is_nhn(n): return n.startswith('한게임')

# ============================================================
# 1) 연령 라인 차트
# ============================================================
def build_age_chart():
    W, H = 720, 280
    left, right, top, bot = 60, 620, 40, 230
    def yc(v): return top + (bot-top) * (1 - (v-25)/25)  # 25~50세 범위
    xs = [left + i*((right-left)/4) for i in range(5)]

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:900px;height:auto;display:block;margin:8px 0;">']
    # grid
    for gv in [25,30,35,40,45,50]:
        y = yc(gv)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#94a3b8">{gv}세</text>')
    # X labels
    for i, yr in enumerate(YEARS):
        c = '#f59e0b' if yr=='26.1Q' else '#64748b'
        w = '800' if yr=='26.1Q' else '600'
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+20}" text-anchor="middle" font-size="11" fill="{c}" font-weight="{w}">{yr}</text>')
    # Lines
    for game in GAMES:
        color = COLORS[game]
        ages = []
        for yr in YEARS:
            a = D[game].get(yr, {}).get('age')
            ages.append(a)
        # Draw line only for non-null points
        pts_non_null = [(xs[i], yc(ages[i])) for i in range(5) if ages[i] is not None]
        if len(pts_non_null) >= 2:
            pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts_non_null)
            svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="{"2.5" if is_nhn(game) else "2"}" points="{pts_str}" opacity="{"1" if is_nhn(game) else "0.7"}"/>')
        for i, a in enumerate(ages):
            if a is not None:
                svg.append(f'<circle cx="{xs[i]:.1f}" cy="{yc(a):.1f}" r="3.5" fill="{color}"/>')

    # Legend (오른쪽)
    legend_x = right + 10
    for i, game in enumerate(GAMES):
        y = top + i * 22
        color = COLORS[game]
        fw = '700' if is_nhn(game) else '400'
        svg.append(f'<rect x="{legend_x}" y="{y}" width="12" height="3" fill="{color}"/>')
        svg.append(f'<text x="{legend_x+17}" y="{y+5}" font-size="9" fill="{color}" font-weight="{fw}">{game}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# ============================================================
# 2) 남녀 비중 수평 누적 막대 (26.1Q 기준)
# ============================================================
def build_gender_chart():
    W, H = 720, 280
    bar_h = 20
    row_gap = 12
    left, right, top = 160, 600, 40
    total_w = right - left

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:900px;height:auto;display:block;margin:8px 0;">']
    # title hint
    svg.append(f'<text x="{(left+right)/2}" y="20" text-anchor="middle" font-size="11" fill="#475569" font-weight="600">26.1Q 기준 · M(파랑) / F(분홍)</text>')
    for i, game in enumerate(GAMES):
        y = top + i * (bar_h + row_gap)
        d = D[game].get('26.1Q', {})
        m = d.get('m_pct'); f = d.get('f_pct')
        name_color = '#0085ca' if is_nhn(game) else '#475569'
        fw = '700' if is_nhn(game) else '500'
        svg.append(f'<text x="{left-8}" y="{y+bar_h/2+4}" text-anchor="end" font-size="11" fill="{name_color}" font-weight="{fw}">{game}</text>')
        if m is None or f is None:
            svg.append(f'<rect x="{left}" y="{y}" width="{total_w}" height="{bar_h}" fill="#f1f5f9" rx="3"/>')
            svg.append(f'<text x="{left+total_w/2}" y="{y+bar_h/2+4}" text-anchor="middle" font-size="10" fill="#cbd5e1">데이터 없음</text>')
            continue
        m_w = total_w * m / 100
        f_w = total_w * f / 100
        svg.append(f'<rect x="{left}" y="{y}" width="{m_w:.1f}" height="{bar_h}" fill="#3b82f6" rx="3"/>')
        svg.append(f'<rect x="{left+m_w:.1f}" y="{y}" width="{f_w:.1f}" height="{bar_h}" fill="#ec4899" rx="3"/>')
        # 값 라벨
        svg.append(f'<text x="{left+m_w/2:.1f}" y="{y+bar_h/2+4}" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">M {m:.0f}%</text>')
        svg.append(f'<text x="{left+m_w+f_w/2:.1f}" y="{y+bar_h/2+4}" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">F {f:.0f}%</text>')
    svg.append('</svg>')
    return '\n'.join(svg)

# ============================================================
# 3) MAU 테이블 + 합계
# ============================================================
def build_metric_table(title, key, color='#f59e0b'):
    rows = []
    sums = {y: 0 for y in YEARS}
    counts = {y: 0 for y in YEARS}
    for game in GAMES:
        row_bg = 'background:#eff6ff;' if is_nhn(game) else ''
        name_color = '#0085ca' if is_nhn(game) else '#1e293b'
        fw = '700' if is_nhn(game) else '500'
        tds = [f'<td style="padding:5px 8px;font-size:0.72rem;color:{name_color};font-weight:{fw};{row_bg}">{game}</td>']
        for yr in YEARS:
            v = D[game].get(yr, {}).get(key)
            is_26 = yr == '26.1Q'
            bg = 'background:#fef3c7;' if is_26 else row_bg
            if v is None:
                txt = '<span style="color:#cbd5e1;">-</span>'
            else:
                txt = f'{v:.1f}'
                sums[yr] += v
                counts[yr] += 1
            tds.append(f'<td class="num" style="padding:5px 8px;font-size:0.72rem;{bg}">{txt}</td>')
        rows.append('            <tr>' + ''.join(tds) + '</tr>')

    # 합계 행
    tot_tds = [f'<td style="padding:5px 8px;font-size:0.72rem;color:#0f172a;font-weight:700;background:#f8fafc;">합계 (7게임)</td>']
    for yr in YEARS:
        is_26 = yr == '26.1Q'
        bg = 'background:#fef3c7;' if is_26 else 'background:#f8fafc;'
        txt = f'{sums[yr]:.1f}' if sums[yr] else '-'
        tot_tds.append(f'<td class="num" style="padding:5px 8px;font-size:0.72rem;{bg}font-weight:700;">{txt}</td>')
    rows.append('            <tr>' + ''.join(tot_tds) + '</tr>')

    thead = ('<thead><tr>'
             '<th style="text-align:left;padding:6px 8px;background:#f8fafc;font-size:0.7rem;">게임</th>'
             + ''.join(f'<th class="num" style="padding:6px 8px;background:#fbbf24;color:#78350f;font-size:0.7rem;">{y}</th>' if y=='26.1Q'
                       else f'<th class="num" style="padding:6px 8px;background:#f8fafc;font-size:0.7rem;">\'{y[-2:]}</th>' for y in YEARS)
             + '</tr></thead>')

    return (f'<div style="border:1px solid #e2e8f0;border-radius:8px;padding:10px 12px;background:#fff;">\n'
            f'  <div style="font-size:0.82rem;font-weight:700;color:{color};margin-bottom:8px;">{title}</div>\n'
            f'  <table style="width:100%;border-collapse:collapse;">\n'
            f'    {thead}\n    <tbody>\n'
            + '\n'.join(rows) + '\n'
            f'    </tbody>\n  </table>\n</div>')

age_chart = build_age_chart()
gender_chart = build_gender_chart()
mau_table = build_metric_table('📊 월평균 MAU (만명)', 'mau_man', '#f59e0b')
dl_table = build_metric_table('📥 월평균 다운로드 (만건)', 'dl_man', '#059669')

demographics_block = f'''
    <div style="margin-top:20px;">
      <h4 style="font-size:0.95rem;font-weight:700;color:#0f172a;margin-bottom:8px;padding:8px 12px;background:linear-gradient(90deg,#f1f5f9,transparent);border-left:3px solid #0085ca;border-radius:3px;">📊 7게임 × 연도별 유저/다운로드 비교</h4>

      <!-- 연령 라인 차트 -->
      <div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;background:#fff;margin-bottom:12px;">
        <div style="font-size:0.82rem;font-weight:700;color:#0ea5e9;margin-bottom:6px;">👥 평균 연령 추이 (세)</div>
        {age_chart}
      </div>

      <!-- 남녀 비중 수평 바 -->
      <div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;background:#fff;margin-bottom:12px;">
        <div style="font-size:0.82rem;font-weight:700;color:#ec4899;margin-bottom:6px;">⚧ 남/녀 비중 (26.1Q)</div>
        {gender_chart}
      </div>

      <!-- MAU/DL 테이블 (합계 포함) -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        {mau_table}
        {dl_table}
      </div>

      <div class="ins" style="margin-top:10px;"><strong>핵심:</strong>
        <strong class="nhn">한게임 섯다&맞고 33세</strong>로 7게임 중 가장 젊음 — 고스톱류 중 유일하게 젊은 층 타겟.
        <strong>한게임 신맞고/피망 뉴맞고 44세</strong>는 가장 고령.
        성별: <strong>포커류 M75~80%</strong>로 남성 편중, 고스톱류 <strong>M50~55%</strong>로 성별 균형.
        MAU 합계 26.1Q <strong>61만</strong>으로 전년 대비 회복세, 특히 한게임 포커(15.6만) · 한게임 신맞고(11.6만) 견인.
        다운로드 합계 26.1Q <strong>11.8만건/월</strong>로 신규 유입 급등.
      </div>
      <div class="formula-box" style="margin-top:10px;font-size:0.68rem;">
        <strong>📐 정의/공식</strong><br>
        • 연령/성별: <code>dw_app_monthly</code>의 <code>avg_age_total / female_pct / male_pct</code> (Sensor Tower demographics, 분기→월 forward-fill, 평균)<br>
        • MAU/DL: <code>mau / units</code> 월평균 (만 단위)<br>
        • WPL는 Sensor Tower demographics 미제공 (신규 앱) — 연령/성별 NULL
      </div>
    </div>'''

# ============================================================
# HTML 패치: 기존 demographics 블록 교체
# ============================================================
def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # 기존 demographics 블록 찾기
    old_re = re.compile(
        r'\n    <div style="margin-top:20px;">\s*\n\s*<h4[^>]*>📊 7게임 × 연도별 유저/다운로드 비교</h4>.*?</div>\s*\n    </div>',
        re.DOTALL
    )
    m = old_re.search(wb)
    if m:
        wb = wb[:m.start()] + demographics_block + wb[m.end():]
        print("  [기존 블록 교체]")
    else:
        print("  [기존 블록 못찾음 - 스킵]")

    if is_main: return html[:ws] + wb + html[we:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    o = h.count('<div'); oc = h.count('</div>')
    print(f"\n[{os.path.basename(path)}]")
    h = patch(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"  <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
