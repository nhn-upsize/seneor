# -*- coding: utf-8 -*-
"""
신규 진입 게임 분석 독립 HTML 리포트 생성
- 신규 진입 정의: 각 연도 1월에는 TOP100에 없고, 2~12월 중 처음 진입한 게임
- 국가별 × 연도별 현황
- 국가별 퍼블리셔 및 게임 리스트
"""
import psycopg2, json, os
from collections import defaultdict

OUT = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_newgame_entry.html"
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = [2022, 2023, 2024, 2025, 2026]
COUNTRIES = [('KR','🇰🇷','한국','#3b82f6'),
             ('JP','🇯🇵','일본','#ef4444'),
             ('US','🇺🇸','미국','#a855f7')]

# ============================================================
# 신규 진입 게임 추출 (unified TOP 100, 연도별)
# - 해당 연도 1월에는 없음
# - 2~12월 (or 2~3월 for 2026) 중 처음 진입
# ============================================================
def get_new_entries(country, year):
    # 2026은 3월까지만
    end_month = 3 if year == 2026 else 12
    cur.execute("""
    WITH jan_apps AS (
      SELECT DISTINCT unified_app_id
      FROM dw_app_monthly
      WHERE country=%s AND in_revenue_top100_unified_os=TRUE
        AND date = %s
    ),
    rest_apps AS (
      SELECT DISTINCT ON (unified_app_id)
        unified_app_id, name, publisher_name, publisher_country, date, genre
      FROM dw_app_monthly
      WHERE country=%s AND in_revenue_top100_unified_os=TRUE
        AND date BETWEEN %s AND %s
      ORDER BY unified_app_id, date
    )
    SELECT r.unified_app_id, r.name, r.publisher_name,
           r.publisher_country, r.date, r.genre
    FROM rest_apps r
    WHERE NOT EXISTS (SELECT 1 FROM jan_apps j WHERE j.unified_app_id = r.unified_app_id)
      AND r.unified_app_id IS NOT NULL
    ORDER BY r.date, r.publisher_name
    """, (country, f'{year}-01-01', country, f'{year}-02-01', f'{year}-{end_month:02d}-01'))
    return cur.fetchall()

# 퍼블리셔 국가 그룹 매핑
def pub_group(pub_name, pub_country):
    if pub_name and 'NEXON' in pub_name.upper(): return 'KR'
    if pub_name and 'FUNFLY' in pub_name.upper(): return '중화권'
    if pub_country in ('South Korea',): return 'KR'
    if pub_country in ('Japan',): return 'JP'
    if pub_country in ('China','Hong Kong','Taiwan','Macao'): return '중화권'
    if pub_country in ('US','USA','United States','Canada'): return '북미'
    return '기타'

PG_COLOR = {'KR':'#3b82f6','JP':'#ef4444','중화권':'#f59e0b','북미':'#a855f7','기타':'#64748b'}

# 데이터 수집
print("[쿼리 시작]")
data = {}  # {country: {year: [{uaid, name, pub, pc, grp, date, genre}, ...]}}
counts = defaultdict(lambda: defaultdict(int))  # [country][year] = count
pub_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # [c][y][grp] = count

for cc, _, _, _ in COUNTRIES:
    data[cc] = {}
    for y in YEARS:
        rows = get_new_entries(cc, y)
        items = []
        for uaid, name, pub, pc, d, g in rows:
            grp = pub_group(pub, pc)
            items.append({
                'uaid': uaid, 'name': name or '', 'pub': pub or 'Unknown',
                'pc': pc, 'grp': grp, 'date': str(d), 'genre': g or 'Unknown'
            })
            pub_counts[cc][y][grp] += 1
        data[cc][y] = items
        counts[cc][y] = len(items)
        print(f"  {cc} {y}: {len(items)}개")

cur.close(); conn.close()

# ============================================================
# HTML 빌드
# ============================================================
def fmt_name(n): return n[:32] + ('...' if len(n) > 32 else '')
def fmt_pub(p): return p[:20] + ('...' if len(p) > 20 else '')

# Section 1: 연도별 신규 진입 수 테이블 + 바 차트
section1 = '<div class="section">\n'
section1 += '  <h2>📊 국가별 × 연도별 신규 진입 수</h2>\n'

# 테이블
section1 += '  <table class="summary-table">\n    <thead><tr><th>국가</th>'
for y in YEARS: section1 += f'<th>{y}{" (1~3월)" if y==2026 else ""}</th>'
section1 += '<th>합계 (22~26.1Q)</th></tr></thead>\n    <tbody>\n'
for cc, flag, name, color in COUNTRIES:
    total = sum(counts[cc][y] for y in YEARS)
    section1 += f'      <tr><td style="color:{color};font-weight:700;">{flag} {cc} {name}</td>'
    for y in YEARS:
        section1 += f'<td>{counts[cc][y]}</td>'
    section1 += f'<td style="font-weight:700;background:#f8fafc;">{total}</td></tr>\n'
section1 += '    </tbody>\n  </table>\n'

# 바 차트 (국가별 연도별 묶음)
max_count = max(counts[cc][y] for cc,_,_,_ in COUNTRIES for y in YEARS)
y_max = int((max_count // 10 + 1) * 10)

svg_w, svg_h = 900, 300
left, right, top, bot = 60, 820, 40, 240
xs = [left + i*((right-left)/4) for i in range(5)]
bar_w = 38
group_w = 3 * (bar_w + 3)

chart = [f'<svg viewBox="0 0 {svg_w} {svg_h}" style="width:100%;max-width:1100px;height:auto;display:block;margin:12px 0;">']
# Y grid
for i in range(5):
    v = y_max * i / 4
    y = bot - (bot-top) * v / y_max
    chart.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
    chart.append(f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#94a3b8">{int(v)}</text>')
# Bars
for i, y_lbl in enumerate(YEARS):
    cx = xs[i]
    for j, (cc, flag, name, color) in enumerate(COUNTRIES):
        n = counts[cc][y_lbl]
        bx = cx - group_w/2 + j*(bar_w+3)
        bh = (bot-top) * n / y_max
        by = bot - bh
        chart.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w}" height="{bh:.1f}" fill="{color}" rx="2"/>')
        chart.append(f'<text x="{bx+bar_w/2:.1f}" y="{by-3:.1f}" text-anchor="middle" font-size="9" fill="{color}" font-weight="700">{n}</text>')
    lbl = f'{y_lbl}' + (' (1~3월)' if y_lbl==2026 else '')
    chart.append(f'<text x="{cx:.1f}" y="{bot+18}" text-anchor="middle" font-size="11" fill="#64748b" font-weight="600">{lbl}</text>')
# 범례
for j, (cc, flag, name, color) in enumerate(COUNTRIES):
    x = left + j * 120
    chart.append(f'<rect x="{x}" y="8" width="12" height="12" fill="{color}" rx="2"/>')
    chart.append(f'<text x="{x+17}" y="18" font-size="11" fill="{color}" font-weight="700">{flag} {cc} {name}</text>')
chart.append('</svg>')
section1 += '  <div class="chart-wrap">' + ''.join(chart) + '</div>\n</div>\n'

# Section 2~4: 국가별 상세 (퍼블리셔별 수 + 게임 리스트)
country_sections = ''
for cc, flag, name, color in COUNTRIES:
    country_sections += f'\n<div class="section" style="border-top:4px solid {color};">\n'
    country_sections += f'  <h2 style="color:{color};">{flag} {cc} {name} — 신규 진입 상세</h2>\n'

    # 퍼블리셔 그룹별 연도 테이블
    pub_groups_all = ['KR','JP','중화권','북미','기타']
    country_sections += '  <h3>퍼블리셔 국적별 신규 진입 수</h3>\n'
    country_sections += '  <table class="pub-table">\n    <thead><tr><th>퍼블 국적</th>'
    for y in YEARS: country_sections += f'<th>{y}</th>'
    country_sections += '<th>합계</th></tr></thead>\n    <tbody>\n'
    for grp in pub_groups_all:
        total = sum(pub_counts[cc][y][grp] for y in YEARS)
        if total == 0: continue
        grp_color = PG_COLOR[grp]
        country_sections += f'      <tr><td style="color:{grp_color};font-weight:700;">{grp}</td>'
        for y in YEARS:
            v = pub_counts[cc][y][grp]
            country_sections += f'<td>{v if v > 0 else "-"}</td>'
        country_sections += f'<td style="font-weight:700;background:#f8fafc;">{total}</td></tr>\n'
    country_sections += '    </tbody>\n  </table>\n'

    # 연도별 게임 리스트 (아코디언 스타일)
    country_sections += '  <h3>연도별 신규 진입 게임 리스트</h3>\n'
    for y in YEARS:
        items = data[cc][y]
        if not items: continue
        y_lbl = f'{y}' + (' (1~3월)' if y==2026 else '')
        country_sections += f'  <details open>\n    <summary><strong>{y_lbl}</strong> · 총 <strong>{len(items)}개</strong> 신규 진입</summary>\n'
        country_sections += '    <table class="game-table">\n'
        country_sections += '      <thead><tr><th>게임명</th><th>퍼블리셔</th><th>퍼블 국적</th><th>장르</th><th>진입월</th></tr></thead>\n      <tbody>\n'
        for it in items:
            grp_color = PG_COLOR[it['grp']]
            country_sections += f'        <tr><td>{fmt_name(it["name"])}</td>'
            country_sections += f'<td>{fmt_pub(it["pub"])}</td>'
            country_sections += f'<td style="color:{grp_color};font-weight:600;">{it["grp"]}</td>'
            country_sections += f'<td>{it["genre"]}</td>'
            country_sections += f'<td>{it["date"][:7]}</td></tr>\n'
        country_sections += '      </tbody>\n    </table>\n  </details>\n'

    country_sections += '</div>\n'

# 전체 HTML
html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>신규 진입 게임 분석 — KR/JP/US</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Noto Sans KR',sans-serif; background:#fafbfc; color:#1e293b; padding:28px 24px; line-height:1.5; }}
  .container {{ max-width:1280px; margin:0 auto; }}
  h1 {{ font-size:1.6rem; font-weight:800; text-align:center; margin-bottom:8px; color:#0f172a; }}
  .subtitle {{ text-align:center; font-size:0.82rem; color:#94a3b8; margin-bottom:24px; }}
  .definition {{ background:#fef3c7; border-left:4px solid #d97706; padding:14px 18px; border-radius:6px; margin-bottom:24px; }}
  .definition strong {{ color:#78350f; }}
  .section {{ background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:20px 24px; margin-bottom:20px; }}
  h2 {{ font-size:1.1rem; font-weight:800; color:#0f172a; margin-bottom:12px; }}
  h3 {{ font-size:0.95rem; font-weight:700; color:#475569; margin:18px 0 8px; padding:6px 10px; background:#f8fafc; border-left:3px solid #64748b; border-radius:3px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.78rem; margin-top:8px; }}
  th {{ background:#f1f5f9; padding:8px 12px; text-align:left; font-weight:700; color:#475569; border-bottom:2px solid #e2e8f0; }}
  td {{ padding:7px 12px; border-bottom:1px solid #f1f5f9; color:#475569; }}
  table.summary-table td, table.summary-table th {{ text-align:center; }}
  table.summary-table td:first-child, table.summary-table th:first-child {{ text-align:left; }}
  table.pub-table td, table.pub-table th {{ text-align:center; }}
  table.pub-table td:first-child, table.pub-table th:first-child {{ text-align:left; }}
  table.game-table {{ font-size:0.73rem; margin-top:6px; }}
  details {{ margin:8px 0; border:1px solid #e2e8f0; border-radius:6px; padding:10px 14px; background:#fafbfc; }}
  summary {{ cursor:pointer; font-size:0.85rem; padding:4px 0; color:#475569; }}
  summary:hover {{ color:#0f172a; }}
  .chart-wrap {{ overflow-x:auto; }}
</style>
</head>
<body>
<div class="container">
  <h1>🆕 KR/JP/US 신규 진입 게임 분석</h1>
  <p class="subtitle">in_revenue_top100_unified_os=TRUE · 2022~2026.1Q · OS 통합 기준</p>

  <div class="definition">
    <strong>📌 신규 진입 정의</strong><br>
    각 연도별 TOP 100에 <strong>2~12월 중 처음 진입</strong>한 게임 (1월은 전년도 잔류 게임과 구분이 어려워 제외).<br>
    2026년은 <strong>2~3월 (26.1Q)</strong> 기준으로만 집계.<br>
    동일 unified_app_id(iOS+Android 통합 ID) 기준으로 중복 제거.
  </div>

  {section1}

  {country_sections}

  <div style="text-align:center;color:#94a3b8;font-size:0.72rem;margin-top:20px;padding:12px;border-top:1px solid #e2e8f0;">
    출처: dw_app_monthly · Sensor Tower · 2022-01 ~ 2026-03 수집 데이터<br>
    퍼블 국적 분류: NEXON→KR, FUNFLY→중화권 강제
  </div>
</div>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f: f.write(html)
print(f"\n[저장] {OUT}")
print(f"[크기] {os.path.getsize(OUT)/1024:.1f} KB")
