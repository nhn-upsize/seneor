# -*- coding: utf-8 -*-
"""신규 진입 게임 분석 v2 — 국가별 탭 구조 + 월평균 추가"""
import psycopg2, os
from collections import defaultdict

OUT = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_newgame_entry.html"
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = [2022, 2023, 2024, 2025, 2026]
MONTHS_PER_YEAR = {2022:11, 2023:11, 2024:11, 2025:11, 2026:2}  # 2~12월 (2026은 2~3월)
COUNTRIES = [('KR','🇰🇷','한국','#3b82f6','#dbeafe'),
             ('JP','🇯🇵','일본','#ef4444','#fee2e2'),
             ('US','🇺🇸','미국','#a855f7','#f3e8ff')]

def get_new_entries(country, year):
    end_month = 3 if year == 2026 else 12
    cur.execute("""
    WITH jan_apps AS (
      SELECT DISTINCT unified_app_id
      FROM dw_app_monthly
      WHERE country=%s AND in_revenue_top100_unified_os=TRUE AND date=%s
    ),
    rest AS (
      SELECT DISTINCT ON (unified_app_id)
        unified_app_id, name, publisher_name, publisher_country, date, genre
      FROM dw_app_monthly
      WHERE country=%s AND in_revenue_top100_unified_os=TRUE
        AND date BETWEEN %s AND %s
      ORDER BY unified_app_id, date
    )
    SELECT r.unified_app_id, r.name, r.publisher_name, r.publisher_country, r.date, r.genre
    FROM rest r
    WHERE NOT EXISTS (SELECT 1 FROM jan_apps j WHERE j.unified_app_id=r.unified_app_id)
      AND r.unified_app_id IS NOT NULL
    ORDER BY r.date, r.publisher_name
    """, (country, f'{year}-01-01', country, f'{year}-02-01', f'{year}-{end_month:02d}-01'))
    return cur.fetchall()

def pub_group(pub_name, pub_country):
    if pub_name and 'NEXON' in pub_name.upper(): return 'KR'
    if pub_name and 'FUNFLY' in pub_name.upper(): return '중화권'
    if pub_country in ('South Korea',): return 'KR'
    if pub_country in ('Japan',): return 'JP'
    if pub_country in ('China','Hong Kong','Taiwan','Macao'): return '중화권'
    if pub_country in ('US','USA','United States','Canada'): return '북미'
    return '기타'

PG_COLOR = {'KR':'#3b82f6','JP':'#ef4444','중화권':'#f59e0b','북미':'#a855f7','기타':'#64748b'}

print("[쿼리]")
data = {}
counts = defaultdict(lambda: defaultdict(int))
pub_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for cc, *_ in COUNTRIES:
    data[cc] = {}
    for y in YEARS:
        rows = get_new_entries(cc, y)
        items = []
        for uaid, name, pub, pc, d, g in rows:
            grp = pub_group(pub, pc)
            items.append({'uaid':uaid,'name':name or '','pub':pub or 'Unknown',
                          'pc':pc,'grp':grp,'date':str(d),'genre':g or 'Unknown'})
            pub_counts[cc][y][grp] += 1
        data[cc][y] = items
        counts[cc][y] = len(items)
    print(f"  {cc}: {[counts[cc][y] for y in YEARS]}")

cur.close(); conn.close()

def fmt_name(n): return n[:35] + ('...' if len(n) > 35 else '')
def fmt_pub(p): return p[:22] + ('...' if len(p) > 22 else '')

# ============================================================
# 국가별 탭 콘텐츠
# ============================================================
def build_country_panel(cc, flag, name, color, color_light, is_active):
    items = data[cc]
    total = sum(counts[cc][y] for y in YEARS)
    total_months = sum(MONTHS_PER_YEAR[y] for y in YEARS)
    avg_monthly = total / total_months if total_months else 0

    # 요약 카드 (전체 + 월평균)
    summary = f'''
  <div class="summary-cards">
    <div class="card" style="border-top-color:{color};">
      <div class="card-label">전체 신규 진입 수 (22~26.1Q)</div>
      <div class="card-value" style="color:{color};">{total}<span class="unit">개</span></div>
      <div class="card-sub">총 {total_months}개월 분석 대상 (2~12월 × 4년 + 2~3월)</div>
    </div>
    <div class="card" style="border-top-color:{color};">
      <div class="card-label">월평균 신규 진입 수</div>
      <div class="card-value" style="color:{color};">{avg_monthly:.1f}<span class="unit">개/월</span></div>
      <div class="card-sub">연도별 평균 {total/5:.0f}개/년 진입</div>
    </div>
  </div>'''

    # 연도별 수치 표
    yearly_table = '''
  <h3>연도별 신규 진입 수</h3>
  <table class="yearly-table">
    <thead><tr><th>연도</th><th>분석 개월</th><th>신규 진입</th><th>월평균</th></tr></thead>
    <tbody>'''
    for y in YEARS:
        n = counts[cc][y]
        m = MONTHS_PER_YEAR[y]
        avg = n/m if m else 0
        y_lbl = f'{y} (1~3월)' if y == 2026 else str(y)
        yearly_table += f'<tr><td><strong>{y_lbl}</strong></td><td>{m}개월</td><td>{n}개</td><td style="color:{color};font-weight:700;">{avg:.1f}개/월</td></tr>'
    yearly_table += '</tbody></table>'

    # 퍼블리셔 국적별 테이블
    pub_section = '<h3>퍼블리셔 국적별 신규 진입 수</h3>\n  <table class="pub-table">\n    <thead><tr><th>퍼블 국적</th>'
    for y in YEARS: pub_section += f'<th>{y}{" 1~3월" if y==2026 else ""}</th>'
    pub_section += '<th>합계</th><th>월평균</th></tr></thead>\n    <tbody>'
    for grp in ['KR','JP','중화권','북미','기타']:
        total_g = sum(pub_counts[cc][y][grp] for y in YEARS)
        if total_g == 0: continue
        grp_color = PG_COLOR[grp]
        avg_g = total_g / total_months
        pub_section += f'<tr><td style="color:{grp_color};font-weight:700;">{grp}</td>'
        for y in YEARS:
            v = pub_counts[cc][y][grp]
            pub_section += f'<td>{v if v>0 else "-"}</td>'
        pub_section += f'<td style="font-weight:700;background:#f8fafc;">{total_g}</td>'
        pub_section += f'<td style="color:{grp_color};font-weight:600;">{avg_g:.1f}개/월</td></tr>'
    pub_section += '</tbody></table>'

    # 연도별 게임 리스트 (아코디언)
    game_lists = '<h3>연도별 신규 진입 게임 리스트</h3>'
    for y in YEARS:
        ys = items[y]
        if not ys: continue
        y_lbl = f'{y} (1~3월)' if y == 2026 else str(y)
        game_lists += f'<details open>\n  <summary><strong>{y_lbl}</strong> · 총 <strong style="color:{color};">{len(ys)}개</strong> 신규 진입 · 월평균 <strong>{len(ys)/MONTHS_PER_YEAR[y]:.1f}개</strong></summary>\n'
        game_lists += '<table class="game-table"><thead><tr><th>게임명</th><th>퍼블리셔</th><th>퍼블 국적</th><th>장르</th><th>진입월</th></tr></thead><tbody>'
        for it in ys:
            grp_color = PG_COLOR[it['grp']]
            game_lists += f'<tr><td>{fmt_name(it["name"])}</td>'
            game_lists += f'<td>{fmt_pub(it["pub"])}</td>'
            game_lists += f'<td style="color:{grp_color};font-weight:600;">{it["grp"]}</td>'
            game_lists += f'<td>{it["genre"]}</td>'
            game_lists += f'<td>{it["date"][:7]}</td></tr>'
        game_lists += '</tbody></table></details>'

    active_cls = ' active' if is_active else ''
    return f'''<div class="tab-panel{active_cls}" id="tab-{cc.lower()}" data-color="{color}">
  <div class="tab-content">
    <div class="panel-header" style="background:linear-gradient(90deg,{color_light},transparent);border-left:4px solid {color};">
      <h2 style="color:{color};">{flag} {cc} {name} 시장 — 신규 진입 분석</h2>
    </div>
{summary}
{yearly_table}
{pub_section}
{game_lists}
  </div>
</div>'''

# 3개 탭 컨텐츠
panels = ''.join(build_country_panel(cc, flag, name, color, cl, i==0)
                 for i, (cc, flag, name, color, cl) in enumerate(COUNTRIES))

# 탭 바
tab_bar = '<div class="tab-bar">'
for i, (cc, flag, name, color, _) in enumerate(COUNTRIES):
    active = ' active' if i == 0 else ''
    total = sum(counts[cc][y] for y in YEARS)
    tab_bar += f'<button class="tab-btn{active}" data-target="tab-{cc.lower()}" data-color="{color}" onclick="switchTab(\'tab-{cc.lower()}\')" style="--tab-color:{color};">'
    tab_bar += f'<span class="flag">{flag}</span><span class="label">{cc} {name}</span>'
    tab_bar += f'<span class="badge" style="background:{color};">{total}개</span>'
    tab_bar += '</button>'
tab_bar += '</div>'

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
  .definition {{ background:#fef3c7; border-left:4px solid #d97706; padding:14px 18px; border-radius:6px; margin-bottom:24px; font-size:0.84rem; }}
  .definition strong {{ color:#78350f; }}

  /* 탭 바 */
  .tab-bar {{ display:flex; gap:8px; margin-bottom:16px; background:#fff; padding:6px; border-radius:10px; border:1px solid #e2e8f0; }}
  .tab-btn {{ flex:1; padding:14px 16px; border:none; background:#f8fafc; border-radius:8px; cursor:pointer; font-family:inherit; font-size:0.9rem; font-weight:700; color:#64748b; display:flex; align-items:center; gap:10px; transition:all 0.2s; border-bottom:3px solid transparent; }}
  .tab-btn:hover {{ background:#f1f5f9; }}
  .tab-btn.active {{ background:#fff; border-bottom-color:var(--tab-color); color:#0f172a; box-shadow:0 2px 6px rgba(0,0,0,0.05); }}
  .tab-btn .flag {{ font-size:1.3rem; }}
  .tab-btn .label {{ flex:1; text-align:left; }}
  .tab-btn .badge {{ color:#fff; padding:2px 10px; border-radius:10px; font-size:0.75rem; font-weight:700; }}

  /* 탭 패널 */
  .tab-panel {{ display:none; }}
  .tab-panel.active {{ display:block; }}
  .panel-header {{ padding:14px 18px; border-radius:6px; margin-bottom:16px; }}
  .panel-header h2 {{ font-size:1.2rem; font-weight:800; }}

  /* 요약 카드 */
  .summary-cards {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:20px; }}
  .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:10px; border-top-width:4px; padding:18px 22px; }}
  .card-label {{ font-size:0.78rem; color:#64748b; font-weight:600; }}
  .card-value {{ font-size:2.4rem; font-weight:800; margin:6px 0 4px; }}
  .card-value .unit {{ font-size:1rem; color:#94a3b8; font-weight:600; margin-left:6px; }}
  .card-sub {{ font-size:0.7rem; color:#94a3b8; }}

  /* 섹션 */
  h3 {{ font-size:0.95rem; font-weight:700; color:#475569; margin:20px 0 8px; padding:8px 12px; background:#f8fafc; border-left:3px solid #64748b; border-radius:3px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.78rem; background:#fff; margin-top:8px; }}
  th {{ background:#f1f5f9; padding:9px 12px; text-align:left; font-weight:700; color:#475569; border-bottom:2px solid #e2e8f0; }}
  td {{ padding:8px 12px; border-bottom:1px solid #f1f5f9; color:#475569; }}
  .yearly-table td, .yearly-table th {{ text-align:center; }}
  .yearly-table td:first-child, .yearly-table th:first-child {{ text-align:left; }}
  .pub-table td, .pub-table th {{ text-align:center; }}
  .pub-table td:first-child, .pub-table th:first-child {{ text-align:left; }}
  .game-table {{ font-size:0.74rem; margin-top:6px; }}
  details {{ margin:10px 0; border:1px solid #e2e8f0; border-radius:6px; padding:12px 16px; background:#fff; }}
  summary {{ cursor:pointer; font-size:0.88rem; padding:4px 0; color:#475569; }}
  summary:hover {{ color:#0f172a; }}
</style>
</head>
<body>
<div class="container">
  <h1>🆕 KR/JP/US 신규 진입 게임 분석</h1>
  <p class="subtitle">in_revenue_top100_unified_os=TRUE · 2022~2026.1Q · OS 통합 기준</p>

  <div class="definition">
    <strong>📌 신규 진입 정의</strong><br>
    각 연도별 TOP 100에 <strong>2~12월 중 처음 진입</strong>한 게임 (1월은 전년도 잔류 구분 어려워 제외).<br>
    <strong>2026년</strong>은 2~3월 (26.1Q) 기준. 동일 unified_app_id(iOS+Android 통합) 기준 중복 제거.<br>
    <strong>월평균</strong> = 신규 진입 수 ÷ 분석 대상 월수 (2022~2025 각 11개월, 2026은 2개월).
  </div>

  {tab_bar}

  {panels}

  <div style="text-align:center;color:#94a3b8;font-size:0.72rem;margin-top:20px;padding:12px;border-top:1px solid #e2e8f0;">
    출처: dw_app_monthly · Sensor Tower · 2022-01 ~ 2026-03 수집 데이터<br>
    퍼블 국적 분류: NEXON→KR, FUNFLY→중화권 강제
  </div>
</div>

<script>
function switchTab(targetId) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(targetId).classList.add('active');
  document.querySelector('[data-target="' + targetId + '"]').classList.add('active');
  window.scrollTo({{top:0, behavior:'smooth'}});
}}
</script>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f: f.write(html)
print(f"\n[저장] {OUT}")
print(f"[크기] {os.path.getsize(OUT)/1024:.1f} KB")
