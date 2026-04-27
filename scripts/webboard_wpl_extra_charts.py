# -*- coding: utf-8 -*-
"""WPL 상세 분석에 추가 3개 차트 (매출 순위/ARPDL/웹보드 점유율)"""
import os, re, json, psycopg2

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# WPL 월별 + 웹보드 전체 월별
cur.execute("""
WITH wpl AS (
  SELECT date, SUM(revenue_krw_100) AS rev, SUM(units) AS dl, MIN(rank_revenue) AS rnk
  FROM dw_app_monthly
  WHERE country='KR' AND name ILIKE '%WPL%' AND publisher_name ILIKE '%Zempot%'
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY date
),
wb AS (
  SELECT date, SUM(revenue_krw_100) AS rev
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND name NOT ILIKE '%모두의마블%' AND name NOT ILIKE '%모두의 마블%'
    AND name NOT ILIKE '%Disney Solitaire%'
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY date
)
SELECT TO_CHAR(wb.date,'YYYY-MM') AS ym,
       COALESCE(wpl.rev, 0)/1e8 AS wpl_rev,
       wb.rev/1e8 AS wb_rev,
       COALESCE(wpl.dl, 0) AS wpl_dl,
       wpl.rnk AS wpl_rank
FROM wb LEFT JOIN wpl USING (date)
ORDER BY wb.date;
""")
data = []
for ym, wpl_rev, wb_rev, wpl_dl, rnk in cur.fetchall():
    wpl_rev = float(wpl_rev or 0); wb_rev = float(wb_rev or 0); wpl_dl = int(wpl_dl or 0)
    arpdl = (wpl_rev * 1e8 / wpl_dl / 10000) if wpl_dl > 0 else 0  # 만원 단위
    share = wpl_rev / wb_rev * 100 if wb_rev > 0 else 0
    data.append({'ym':ym, 'rev':wpl_rev, 'dl':wpl_dl, 'rank':rnk, 'arpdl':arpdl, 'share':share})
cur.close(); conn.close()

# ============================================================
# 차트 SVG 빌더
# ============================================================
def build_chart(title, key, color, unit='', y_min=None, y_max_val=None, y_inverted=False, nullable=True):
    labels = [d['ym'] for d in data]
    values = [d[key] for d in data]

    if y_max_val is None:
        non_null = [v for v in values if v is not None and v > 0]
        y_max_val = max(non_null) if non_null else 1
        if y_max_val < 5: y_max_val = 5
        elif y_max_val < 20: y_max_val = int((y_max_val//5+1)*5)
        else: y_max_val = int((y_max_val//10+1)*10)
    if y_min is None: y_min = 0

    W = 860; H = 260
    left, right, top, bot = 60, 830, 40, 210

    def yc(v):
        if v is None: return None
        if y_inverted:
            return top + (bot-top) * ((v-y_min)/(y_max_val-y_min))
        return top + (bot-top) * (1 - (v-y_min)/(y_max_val-y_min))

    xs = [left + i*((right-left)/(len(labels)-1)) for i in range(len(labels))]

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:1040px;height:auto;display:block;margin:6px 0;">']
    svg.append(f'<text x="{(left+right)/2}" y="18" text-anchor="middle" font-size="12" fill="#475569" font-weight="700">{title}</text>')

    # Y grid
    for i in range(6):
        gv = y_min + (y_max_val-y_min) * i / 5
        y = yc(gv)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-4}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{gv:.0f}{unit}</text>')

    # Year dividers
    years_seen = set()
    for i, lbl in enumerate(labels):
        yr = lbl.split('-')[0]
        if yr not in years_seen:
            years_seen.add(yr)
            svg.append(f'<line x1="{xs[i]:.1f}" y1="{top}" x2="{xs[i]:.1f}" y2="{bot}" stroke="#e2e8f0" stroke-dasharray="3,3"/>')
            c = '#f59e0b' if yr=='2026' else '#64748b'
            w = '800' if yr=='2026' else '600'
            svg.append(f'<text x="{xs[i]+5:.1f}" y="{top+12}" font-size="10" fill="{c}" font-weight="{w}">{yr}</text>')
    for i, lbl in enumerate(labels):
        if i % 6 == 0:
            svg.append(f'<text x="{xs[i]:.1f}" y="{bot+14}" text-anchor="middle" font-size="8" fill="#94a3b8">{lbl[2:]}</text>')

    # Line (skip NULL)
    pts = [(xs[i], yc(values[i])) for i in range(len(values)) if values[i] is not None and (values[i] > 0 or not nullable)]
    if len(pts) >= 2:
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
        svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts_str}"/>')
    for i, v in enumerate(values):
        if v is not None and (v > 0 or not nullable):
            svg.append(f'<circle cx="{xs[i]:.1f}" cy="{yc(v):.1f}" r="2.5" fill="{color}"/>')

    # 최근 3개월 값 라벨
    for i in range(len(values)-3, len(values)):
        v = values[i]
        if v is None or (v == 0 and nullable): continue
        svg.append(f'<text x="{xs[i]:.1f}" y="{yc(v)-8:.1f}" text-anchor="middle" font-size="9" fill="{color}" font-weight="700">{v:.1f}{unit}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# 1) 매출 순위 — y 뒤집힘 (낮은 숫자가 위로)
rank_chart = build_chart('🏆 WPL TOP 100 내 매출 순위 추이 (낮을수록 좋음)', 'rank', '#dc2626',
                         unit='위', y_min=1, y_max_val=100, y_inverted=True, nullable=False)
# rank가 None인 경우 있으므로 특별 처리 — 위 빌더에서 None은 그리지 않음

# 2) ARPDL (만원)
arpdl_chart = build_chart('💰 WPL ARPDL 추이 (만원 = 매출 ÷ 다운로드)', 'arpdl', '#f59e0b',
                          unit='만', y_max_val=40)

# 3) 웹보드 시장 내 점유율 (%)
share_chart = build_chart('📊 WPL 웹보드 시장 내 점유율 (%)', 'share', '#8b5cf6',
                          unit='%', y_max_val=15)

extra_block = f'''
    <!-- 추가 분석 차트 3종 -->
    <h4 style="font-size:0.88rem;font-weight:700;color:#0f172a;margin:18px 0 8px;padding:6px 10px;background:#faf5ff;border-left:3px solid #8b5cf6;border-radius:3px;">🔍 매출 급증 원인 분석 — 순위·ARPDL·점유율</h4>
    <div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px;background:#fff;margin-bottom:10px;">
      {rank_chart}
      <div style="font-size:0.72rem;color:#64748b;margin-top:4px;">↗ 93위(25.7) → <strong style="color:#dc2626;">32위(26.3)</strong>로 61계단 상승. 26.1Q 평균 순위 38위 · 웹보드 상위권 진입</div>
    </div>
    <div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px;background:#fff;margin-bottom:10px;">
      {arpdl_chart}
      <div style="font-size:0.72rem;color:#64748b;margin-top:4px;">다운로드당 매출(유저 1명당 평균 과금) 18만원 → 23만원. <strong>유저 1인당 과금 강도가 +28% 증가</strong>하며 매출 성장 기여</div>
    </div>
    <div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px;background:#fff;">
      {share_chart}
      <div style="font-size:0.72rem;color:#64748b;margin-top:4px;">웹보드 시장 내 비중 2%대 → <strong style="color:#8b5cf6;">10%대</strong>로 급성장. NHN·네오위즈 다음 가는 3위 플레이어로 안착</div>
    </div>

    <div class="ins" style="margin-top:14px;">
      <strong>📌 매출 급증 요인 종합:</strong>
      <ul style="margin:6px 0 0 16px;padding:0;font-size:0.78rem;line-height:1.7;">
        <li><strong>① 다운로드 4.6배 증가</strong> (월 1,754건 → 8,164건) — 신규 유입 폭증</li>
        <li><strong>② ARPDL 28% 증가</strong> (18만원 → 23만원) — 유저 1인당 과금 강화</li>
        <li><strong>③ 매출 순위 61계단 상승</strong> (93위 → 32위) — TOP 100 내 중위권 → 상위권 진입</li>
        <li><strong>④ 웹보드 내 점유율 5배</strong> (2% → 10%) — 시장 핵심 플레이어 등극</li>
      </ul>
      → <strong>유저 증가(신규 유입) × 과금 강화의 복합 효과</strong>로 매출 6배 성장
    </div>'''

# ============================================================
# HTML 패치 — WPL block 내 "데이터 소스" formula-box 직전에 삽입
# ============================================================
def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # 중복 방지
    if '매출 급증 원인 분석' in wb:
        print("  (이미 추가됨)")
        return html if is_main else wb

    # WPL 블록 내 formula-box (데이터 소스) 앞에 삽입
    anchor = wb.find('<strong>📐 데이터 소스</strong>')
    if anchor == -1:
        print("  WPL formula-box 앵커 못찾음")
        return html if is_main else wb
    # 앞에 있는 <div class="formula-box"> 위치
    fb_start = wb.rfind('<div class="formula-box"', 0, anchor)
    wb = wb[:fb_start] + extra_block + '\n    ' + wb[fb_start:]

    if is_main: return html[:ws] + wb + html[we:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    o = h.count('<div'); oc = h.count('</div>')
    h = patch(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
