# -*- coding: utf-8 -*-
"""Section 6에 기타 데이터 추가 + HTML 재생성"""
import os, re, json, psycopg2

DATA_JSON = r"C:\Users\NHN\Documents\sensortower_api\scripts\newgame_data_v2.json"
MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

COMMON_CTE = """
WITH monthly AS (
    SELECT DISTINCT country, unified_app_id, date
    FROM dw_app_monthly
    WHERE in_revenue_top100_unified_os = TRUE
      AND country IN ('KR','JP','US')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
first_entry AS (
    SELECT country, unified_app_id, MIN(date) AS entry_date
    FROM monthly GROUP BY country, unified_app_id
),
new_entries AS (
    SELECT fe.country, fe.unified_app_id, fe.entry_date,
           CASE WHEN fe.entry_date < '2025-01-01' THEN 'before' ELSE 'after' END AS period
    FROM first_entry fe
    WHERE EXTRACT(MONTH FROM fe.entry_date) <> 1
      AND fe.entry_date >= '2022-02-01'
      AND fe.entry_date <= '2026-03-01'
)
"""

with open(DATA_JSON, 'r', encoding='utf-8') as f: D = json.load(f)

# 기타 retention 계산
etc_data = {'before': [], 'after': []}
for period in ['before', 'after']:
    for k in range(1, 13):
        cur.execute(COMMON_CTE + """
        , pub_meta AS (
            SELECT DISTINCT ON (unified_app_id) unified_app_id, publisher_name, publisher_country
            FROM dw_app_monthly
            WHERE in_revenue_top100_unified_os=TRUE AND publisher_country IS NOT NULL
            ORDER BY unified_app_id, date DESC
        ),
        grouped AS (
            SELECT ne.*, CASE
               WHEN pm.publisher_name ILIKE '%%NEXON%%' THEN 'KR'
               WHEN pm.publisher_name ILIKE '%%FUNFLY%%' THEN '중화권'
               WHEN pm.publisher_country IN ('South Korea') THEN 'KR'
               WHEN pm.publisher_country IN ('Japan') THEN 'JP'
               WHEN pm.publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
               WHEN pm.publisher_country IN ('US','USA','United States','Canada') THEN '북미'
               ELSE '기타' END AS pub_grp
            FROM new_entries ne
            LEFT JOIN pub_meta pm ON pm.unified_app_id = ne.unified_app_id
        )
        SELECT
            ROUND(SUM(CASE WHEN EXISTS(
                SELECT 1 FROM monthly m
                WHERE m.country=g.country AND m.unified_app_id=g.unified_app_id
                  AND m.date = g.entry_date + (%s::int || ' months')::interval
            ) THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1)
        FROM grouped g
        WHERE g.pub_grp='기타' AND g.period=%s
          AND g.entry_date + (%s::int || ' months')::interval <= '2026-03-01';
        """, (k, period, k))
        rate = cur.fetchone()[0]
        etc_data[period].append(float(rate) if rate is not None else 0.0)

print("기타 before:", etc_data['before'])
print("기타 after: ", etc_data['after'])

D['section6']['기타'] = etc_data

# 저장
with open(DATA_JSON, 'w', encoding='utf-8') as f:
    json.dump(D, f, ensure_ascii=False, indent=2)

cur.close(); conn.close()

# ============================================================
# HTML Section 6 만 재생성 (기타 포함 5개)
# ============================================================
PUB_GRPS = [('KR','🇰🇷','KR','#3b82f6'),
            ('JP','🇯🇵','JP','#ef4444'),
            ('중화권','','중화권','#f59e0b'),
            ('북미','','북미','#8b5cf6'),
            ('기타','','기타','#64748b')]

def color_diff(delta):
    if delta > 0: return '#059669'
    if delta < 0: return '#dc2626'
    return '#64748b'

def build_retention_svg(before_vals, after_vals, color_after):
    W, H = 620, 240
    left, right, top, bot = 50, 600, 30, 200
    def yc(v): return top + (bot - top) * (1 - v/80)
    grids = ""
    for g in [0, 20, 40, 60, 80]:
        y = yc(g)
        grids += (f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>'
                  f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#94a3b8">{g}%</text>')
    xs = [left + i*((right-left)/11) for i in range(12)]
    before_pts = " ".join(f"{xs[i]:.1f},{yc(before_vals[i]):.1f}" for i in range(12))
    after_pts = " ".join(f"{xs[i]:.1f},{yc(after_vals[i]):.1f}" for i in range(12))
    before_circles = "".join(
        f'<circle cx="{xs[i]:.1f}" cy="{yc(before_vals[i]):.1f}" r="3.5" fill="white" stroke="#94a3b8" stroke-width="1.5"/>'
        for i in range(12))
    after_circles = "".join(
        f'<circle cx="{xs[i]:.1f}" cy="{yc(after_vals[i]):.1f}" r="3.5" fill="{color_after}"/>'
        for i in range(12))
    x_labels = "".join(
        f'<text x="{xs[i]:.1f}" y="216" text-anchor="middle" font-size="10" fill="#64748b">M+{i+1}</text>'
        for i in range(12))
    delta_12 = after_vals[11] - before_vals[11]
    delta_color = color_diff(delta_12)
    delta_txt = f'<text x="{right}" y="14" text-anchor="end" font-size="10" fill="{delta_color}" font-weight="700">M+12 Δ {delta_12:+.1f}%p</text>'
    legend = (
        f'<rect x="50" y="8" width="14" height="3" fill="#94a3b8"/>'
        f'<text x="68" y="14" font-size="10" fill="#475569" font-weight="600">전 (22~24)</text>'
        f'<rect x="140" y="8" width="14" height="3" fill="{color_after}"/>'
        f'<text x="158" y="14" font-size="10" fill="{color_after}" font-weight="700">후 (25~26.1Q)</text>'
    )
    return (
        f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;">'
        f'{grids}'
        f'<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5,3" points="{before_pts}"/>'
        f'{before_circles}'
        f'<polyline fill="none" stroke="{color_after}" stroke-width="2.5" points="{after_pts}"/>'
        f'{after_circles}'
        f'{x_labels}{legend}{delta_txt}'
        f'</svg>'
    )

cards = []
for grp, flag, name, color in PUB_GRPS:
    before = D['section6'][grp]['before']
    after = D['section6'][grp]['after']
    svg = build_retention_svg(before, after, color)
    cards.append(
        f'<div class="ng-card" style="border-top-color:{color};">\n'
        f'  <div class="ng-card-header">\n'
        f'    <span class="ng-flag">{flag}</span>\n'
        f'    <span class="ng-name">{name}</span>\n'
        f'  </div>\n'
        f'  <div class="ng-card-stat" style="padding:8px 10px;">{svg}</div>\n'
        f'</div>'
    )

new_s6 = (
    '<div class="ng-section">\n'
    '  <div class="ng-section-head">\n'
    '    <div class="ng-section-num" style="background:#0f172a;">6</div>\n'
    '    <div>\n'
    '      <h2>📉 퍼블리셔 국적별 차트 잔존율 25년 전후 비교 (M+1 ~ M+12)</h2>\n'
    '      <div class="ng-desc">점선(회색) = 전(22~24 진입) · 실선(컬러) = 후(25~26.1Q 진입) · OS 통합</div>\n'
    '    </div>\n'
    '  </div>\n'
    '  <div class="ng-card-grid cols-5">' + ''.join(cards) + '</div>\n'
    '</div>'
)

with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
o = html.count('<div'); oc = html.count('</div>')

# 기존 Section 6 치환
S6_RE = re.compile(
    r'<div class="ng-section">\s*\n?\s*<div class="ng-section-head">\s*\n?\s*<div class="ng-section-num"[^>]*>6</div>.*?</div>\s*(?=<div class="ng-section">\s*<div class="ng-section-head">\s*<div class="ng-section-num"[^>]*>7</div>|<div class="ng-footer">)',
    re.DOTALL
)
m = S6_RE.search(html)
if not m:
    raise RuntimeError("Section 6 매칭 실패")
html = html[:m.start()] + new_s6 + '\n' + html[m.end():]

with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)
n = html.count('<div'); nc = html.count('</div>')
print(f"<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
