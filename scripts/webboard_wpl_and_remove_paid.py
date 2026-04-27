# -*- coding: utf-8 -*-
"""
1) Step 5 비교 카드에서 광고유입률 행 제거
2) 웹보드 탭 하단에 WPL 월별 매출/DL 시각화 추가
"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\wpl_monthly.json", 'r', encoding='utf-8') as f:
    WPL = json.load(f)

# ============================================================
# WPL 월별 차트 SVG
# ============================================================
def build_line_chart(title, key, color, unit='억'):
    # 48개월 × 값
    labels = [d['ym'] for d in WPL]  # YYYY-MM
    values = [d[key] for d in WPL]
    vmax = max(values) if max(values) > 0 else 1
    # round vmax up
    if vmax < 5: y_max = 5
    elif vmax < 10: y_max = 10
    elif vmax < 20: y_max = 20
    else: y_max = int((vmax // 5 + 1) * 5)

    W = 860; H = 280
    left, right, top, bot = 55, 830, 40, 230

    def yc(v): return top + (bot-top) * (1 - v/y_max)
    # X 위치 (48개월)
    xs = [left + i * ((right-left)/(len(labels)-1)) for i in range(len(labels))]

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:1040px;height:auto;display:block;margin:8px 0;">']
    # Title
    svg.append(f'<text x="{(left+right)/2}" y="18" text-anchor="middle" font-size="12" fill="#475569" font-weight="700">{title}</text>')
    # Y grid
    steps = 5
    for i in range(steps+1):
        gv = y_max * i / steps
        y = yc(gv)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-4}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{gv:.0f}{unit}</text>')
    # Year dividers + labels
    years_seen = set()
    for i, lbl in enumerate(labels):
        yr = lbl.split('-')[0]
        if yr not in years_seen:
            years_seen.add(yr)
            svg.append(f'<line x1="{xs[i]:.1f}" y1="{top}" x2="{xs[i]:.1f}" y2="{bot}" stroke="#e2e8f0" stroke-dasharray="3,3"/>')
            c = '#f59e0b' if yr == '2026' else '#64748b'
            w = '800' if yr == '2026' else '600'
            svg.append(f'<text x="{xs[i]+5:.1f}" y="{top+12}" font-size="10" fill="{c}" font-weight="{w}">{yr}</text>')
    # Monthly labels (every 6개월)
    for i, lbl in enumerate(labels):
        if i % 6 == 0:
            svg.append(f'<text x="{xs[i]:.1f}" y="{bot+14}" text-anchor="middle" font-size="8" fill="#94a3b8">{lbl[2:]}</text>')
    # Line + fill
    pts = [(xs[i], yc(values[i])) for i in range(len(values))]
    pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
    fill_pts = pts_str + f' {xs[-1]:.1f},{yc(0):.1f} {xs[0]:.1f},{yc(0):.1f}'
    grad_id = f'grad-{key}'
    svg.append(f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0%" stop-color="{color}" stop-opacity="0.3"/>'
               f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>')
    svg.append(f'<polygon fill="url(#{grad_id})" points="{fill_pts}"/>')
    svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts_str}"/>')
    # Points + 주요 값 라벨
    for i, v in enumerate(values):
        if v > 0:
            r = 3 if labels[i].startswith('2026') else 2
            svg.append(f'<circle cx="{xs[i]:.1f}" cy="{yc(v):.1f}" r="{r}" fill="{color}"/>')
    # 피크 표시 (2026 값들)
    for i, (lbl, v) in enumerate(zip(labels, values)):
        if lbl.startswith('2026') and v > 0:
            svg.append(f'<text x="{xs[i]:.1f}" y="{yc(v)-8:.1f}" text-anchor="middle" font-size="9" fill="{color}" font-weight="700">{v:.1f}</text>')
    svg.append('</svg>')
    return '\n'.join(svg)

# 매출 차트 + DL 차트
rev_chart = build_line_chart('📈 WPL 월별 매출 추이 (억원)', 'rev', '#8b5cf6', '억')
dl_chart = build_line_chart('📥 WPL 월별 다운로드 추이 (만건)', 'dl', '#3b82f6', '만')

# 연도별 월평균 요약 테이블
YEARS = ['2022','2023','2024','2025','26.1Q']
def year_avg(key):
    result = {}
    for y in YEARS:
        if y == '26.1Q':
            vals = [d[key] for d in WPL if d['ym'].startswith('2026')]
        else:
            vals = [d[key] for d in WPL if d['ym'].startswith(y)]
        result[y] = sum(vals)/len(vals) if vals else 0
    return result

rev_by_yr = year_avg('rev')
dl_by_yr = year_avg('dl')

def build_summary_table():
    rows = []
    for metric_label, data, unit, decimal in [
        ('월평균 매출 (억원)', rev_by_yr, '', 1),
        ('월평균 다운로드 (만건)', dl_by_yr, '', 2),
    ]:
        tds = [f'<td style="padding:6px 10px;font-weight:600;color:#475569;">{metric_label}</td>']
        for y in YEARS:
            v = data[y]
            is_26 = y == '26.1Q'
            bg = 'background:#fef3c7;' if is_26 else ''
            fw = '800' if is_26 else '600'
            txt = f'{v:.{decimal}f}' if v > 0 else '-'
            tds.append(f'<td class="num" style="padding:6px 10px;{bg}font-weight:{fw};">{txt}</td>')
        rows.append('        <tr>' + ''.join(tds) + '</tr>')

    # MAU 행 (N/A)
    tds = ['<td style="padding:6px 10px;font-weight:600;color:#94a3b8;">월평균 MAU (만명)</td>']
    for y in YEARS:
        is_26 = y == '26.1Q'
        bg = 'background:#fef3c7;' if is_26 else ''
        tds.append(f'<td class="num" style="padding:6px 10px;{bg}color:#cbd5e1;">N/A</td>')
    rows.append('        <tr>' + ''.join(tds) + '</tr>')

    thead = ('<thead><tr>'
             '<th style="text-align:left;padding:6px 10px;background:#f8fafc;">지표</th>'
             + ''.join(f'<th class="num" style="padding:6px 10px;background:#fbbf24;color:#78350f;">{y}</th>' if y=='26.1Q'
                       else f'<th class="num" style="padding:6px 10px;background:#f8fafc;">\'{y[-2:]}</th>' for y in YEARS)
             + '</tr></thead>')
    return ('<table style="width:100%;border-collapse:collapse;font-size:0.78rem;">\n'
            f'      {thead}\n'
            '      <tbody>\n'
            + '\n'.join(rows) + '\n'
            '      </tbody>\n    </table>')

summary_table = build_summary_table()

# WPL 전체 블록
wpl_block = f'''
<!-- WPL 상세 분석 -->
<div class="step" style="border-top:3px solid #8b5cf6;">
  <div class="step-head">
    <div class="step-num" style="background:#8b5cf6;">⚡</div>
    <div class="step-info">
      <div class="step-q">WPL (윈조이 포커 리그) 월별 상세 분석 <span style="font-size:0.7rem;color:#64748b;font-weight:500;">(Zempot — 신흥 위협)</span></div>
      <div class="step-a">25년 9월부터 <strong style="color:#8b5cf6;">3.7억 → 13.4억 → 16억대</strong>로 급성장, 26.1Q 월평균 <strong>18.4억</strong> · TOP 3위권 진입</div>
    </div>
  </div>
  <div class="step-body">
    <!-- 요약 테이블 -->
    <h4 style="font-size:0.88rem;font-weight:700;color:#0f172a;margin:8px 0;padding:6px 10px;background:#faf5ff;border-left:3px solid #8b5cf6;border-radius:3px;">📊 연도별 월평균 요약</h4>
    {summary_table}

    <!-- 매출 차트 -->
    <div style="margin-top:18px;border:1px solid #e2e8f0;border-radius:8px;padding:12px;background:#fff;">
      {rev_chart}
    </div>

    <!-- 다운로드 차트 -->
    <div style="margin-top:10px;border:1px solid #e2e8f0;border-radius:8px;padding:12px;background:#fff;">
      {dl_chart}
    </div>

    <div class="ins" style="margin-top:12px;">
      <strong>핵심:</strong> WPL은 <strong>22~24년 간헐적 진입(연 2~4개월)</strong>에서 <strong>25년 2월부터 꾸준히 TOP 100 유지</strong>.
      결정적 전환은 <strong style="color:#8b5cf6;">25년 9월 3.7억 → 13.4억 (3.6배 급등)</strong> — 이후 16~19억대 정착.
      26.1Q 월평균 <strong>18.4억</strong>로 웹보드 전체 4위 수준까지 도달, NHN·네오위즈 구도에 본격 진입.
      <br>다운로드도 월 0.2만→0.8만으로 4배 증가, 신규 유입이 성장 드라이버.
    </div>
    <div class="formula-box" style="font-size:0.68rem;">
      <strong>📐 데이터 소스</strong><br>
      • 매출: <code>revenue_krw_100</code> (ST 100% 보정 + 연도별 환율)<br>
      • 다운로드: <code>units</code> (Sensor Tower 추정)<br>
      • MAU: Sensor Tower가 Zempot 앱 미추정 (N/A) — active_users 수집 대상 밖<br>
      • 대상: WPL:Texas Hold'em (android) + WPL(윈조이 포커 리그) (iOS) 합산
    </div>
  </div>
</div>'''

# ============================================================
# HTML 패치
# ============================================================
def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # 1) 광고유입률 행 제거 (Step 5 카드 4개)
    # 패턴: <div class="compare-stat"><span>광고유입률</span>...</div>
    wb = re.sub(
        r'\s*<div class="compare-stat"><span>광고유입률</span>[^<]*<strong>[^<]*</strong></div>',
        '', wb
    )

    # 2) 중복 삽입 방지
    if 'WPL (윈조이 포커 리그) 월별 상세 분석' in wb:
        print("  (WPL 블록 이미 있음)")
    else:
        # 웹보드 탭 마지막 conclusion 바로 앞에 WPL 블록 삽입
        concl_start = wb.rfind('<div class="conclusion">')
        if concl_start == -1:
            # 맨 끝에 붙이기
            insert_pos = len(wb)
        else:
            insert_pos = concl_start
        wb = wb[:insert_pos] + wpl_block + '\n\n' + wb[insert_pos:]

    if is_main: return html[:ws] + wb + html[we:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_wpl'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o = h.count('<div'); oc = h.count('</div>')
    h = patch(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
