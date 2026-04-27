# -*- coding: utf-8 -*-
"""
3국 신규 진입 & 3개월 생존 분석 (newgame_entry_survival.html 형식 확장)
- KR/JP/US 탭 구조
- Part 1 물량 / Part 2 생존율 / Part 3 요약
- 정의: 전체 기간(2022.01~2026.03) 중 unified TOP100 최초 진입월 (1월 제외, 재진입 미카운트)
"""
import psycopg2, os
from collections import defaultdict

OUT = r"C:\Users\NHN\Documents\sensortower_api\reports\newgame_survival_3country.html"
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = [2022, 2023, 2024, 2025, 2026]
YEAR_MONTHS = {2022:11, 2023:11, 2024:11, 2025:11, 2026:2}
COUNTRIES = [('KR','🇰🇷','한국','#3b82f6','#dbeafe'),
             ('JP','🇯🇵','일본','#ef4444','#fee2e2'),
             ('US','🇺🇸','미국','#a855f7','#f3e8ff')]

def pub_group(name, pc):
    if name and 'NEXON' in name.upper(): return 'KR'
    if name and 'FUNFLY' in name.upper(): return '중화권'
    if pc == 'South Korea': return 'KR'
    if pc == 'Japan': return 'JP'
    if pc in ('China','Hong Kong','Taiwan','Macao'): return '중화권'
    if pc in ('US','USA','United States','Canada'): return '북미'
    return '기타'

PG_ORDER = ['KR','JP','중화권','북미','기타']
PG_COLOR = {'KR':'#3b82f6','JP':'#ef4444','중화권':'#f59e0b','북미':'#a855f7','기타':'#64748b'}

# ============================================================
# 전체 기간 최초 진입 + 생존 여부
# ============================================================
print("[쿼리 시작]")
cur.execute("""
WITH first_entry AS (
  SELECT country, unified_app_id, MIN(date) AS first_date
  FROM dw_app_monthly
  WHERE country IN ('KR','JP','US') AND in_revenue_top100_unified_os=TRUE
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY country, unified_app_id
),
filtered AS (
  SELECT country, unified_app_id, first_date
  FROM first_entry
  WHERE EXTRACT(MONTH FROM first_date) <> 1
),
meta AS (
  SELECT DISTINCT ON (country, unified_app_id)
    country, unified_app_id, name, publisher_name, publisher_country, genre
  FROM dw_app_monthly
  WHERE country IN ('KR','JP','US') AND in_revenue_top100_unified_os=TRUE
  ORDER BY country, unified_app_id, date DESC
)
SELECT f.country, f.unified_app_id, f.first_date,
       m.name, m.publisher_name, m.publisher_country, m.genre,
       EXISTS(
         SELECT 1 FROM dw_app_monthly d
         WHERE d.country=f.country AND d.unified_app_id=f.unified_app_id
           AND d.date = f.first_date + INTERVAL '3 months'
           AND d.in_revenue_top100_unified_os=TRUE
       ) AS survived,
       (f.first_date + INTERVAL '3 months' <= '2026-03-01') AS measurable
FROM filtered f
JOIN meta m ON m.country=f.country AND m.unified_app_id=f.unified_app_id
ORDER BY f.country, f.first_date;
""")

# 데이터 구조화
rows = cur.fetchall()
print(f"[전체 로우] {len(rows)}")

data = defaultdict(list)  # data[country] = [entries]
for country, uaid, fd, name, pub, pc, genre, survived, measurable in rows:
    y = fd.year
    grp = pub_group(pub, pc)
    data[country].append({
        'uaid': uaid, 'first_date': fd, 'year': y,
        'name': name or '', 'pub': pub or 'Unknown', 'pc': pc,
        'genre': genre or 'Unknown', 'grp': grp,
        'survived': survived, 'measurable': measurable,
    })

# 통계 집계
for cc in ['KR','JP','US']:
    stats = defaultdict(lambda: defaultdict(int))
    for e in data[cc]:
        y = e['year']
        stats[y]['total'] += 1
        if e['genre'] == 'Role Playing': stats[y]['rpg'] += 1
        stats[y][f'grp_{e["grp"]}'] += 1
    print(f"\n[{cc}]")
    for y in YEARS:
        t = stats[y]['total']
        rpg = stats[y]['rpg']
        pct = rpg/t*100 if t else 0
        print(f"  {y}: 총 {t}개, RPG {rpg} ({pct:.1f}%)")

cur.close(); conn.close()

# ============================================================
# HTML 빌더
# ============================================================
def fmt_name(n): return (n[:35] + '...') if len(n) > 35 else n
def fmt_pub(p): return (p[:22] + '...') if len(p) > 22 else p

def build_panel(cc, flag, cname, color, color_light, is_active):
    entries = data[cc]

    # ==== PART 1: 물량 ====
    # 연도별 전체 + RPG 비중
    yearly = defaultdict(lambda: {'total':0, 'rpg':0, 'grp':defaultdict(int), 'genre':defaultdict(int)})
    for e in entries:
        y = e['year']
        yearly[y]['total'] += 1
        if e['genre'] == 'Role Playing': yearly[y]['rpg'] += 1
        yearly[y]['grp'][e['grp']] += 1
        yearly[y]['genre'][e['genre']] += 1

    # 1-1 전체 테이블
    p1_1 = '<h3>1-1. 전체</h3>\n<table>\n<tr><th>연도</th><th>월평균 신규진입</th><th>신규진입 (총합)</th><th>RPG 비중</th></tr>\n'
    for y in YEARS:
        t = yearly[y]['total']; rpg = yearly[y]['rpg']; m = YEAR_MONTHS[y]
        avg = t/m if m else 0; pct = rpg/t*100 if t else 0
        y_lbl = f'{y} 1Q' if y == 2026 else str(y)
        t_lbl = f'{t} ({m}개월)' if y == 2026 else str(t)
        p1_1 += f'<tr><td>{y_lbl}</td><td>{avg:.1f}</td><td>{t_lbl}</td><td>{pct:.1f}%</td></tr>\n'
    p1_1 += '</table>\n'

    # 1-2 퍼블리셔 그룹별
    p1_2 = '<h3>1-2. 퍼블리셔 그룹별 신규진입 수</h3>\n<table>\n<tr><th>퍼블 국적</th>'
    for y in YEARS: p1_2 += f'<th>{y}{"Q1" if y==2026 else ""}</th>'
    p1_2 += '<th>합계</th></tr>\n'
    for g in PG_ORDER:
        total_g = sum(yearly[y]['grp'][g] for y in YEARS)
        if total_g == 0: continue
        p1_2 += f'<tr><td class="left" style="color:{PG_COLOR[g]};font-weight:700;">{g}</td>'
        for y in YEARS:
            v = yearly[y]['grp'][g]
            p1_2 += f'<td>{v if v else "-"}</td>'
        p1_2 += f'<td style="font-weight:700;background:#f8fafc;">{total_g}</td></tr>\n'
    p1_2 += '</table>\n'

    # 1-3 장르 구성 변화 (Top 5 장르 + 기타)
    all_genres = defaultdict(int)
    for e in entries: all_genres[e['genre']] += 1
    top_g = [g for g,_ in sorted(all_genres.items(), key=lambda x:-x[1])[:5]]
    p1_3 = '<h3>1-3. 장르 구성 변화 (Top 5)</h3>\n<table>\n<tr><th>장르</th>'
    for y in YEARS: p1_3 += f'<th>{y}{"Q1" if y==2026 else ""}</th>'
    p1_3 += '<th>합계</th></tr>\n'
    for g in top_g:
        total_g = sum(yearly[y]['genre'][g] for y in YEARS)
        p1_3 += f'<tr><td class="left"><strong>{g}</strong></td>'
        for y in YEARS:
            v = yearly[y]['genre'][g]
            t = yearly[y]['total']
            pct = v/t*100 if t else 0
            p1_3 += f'<td>{v}<br><span style="color:#94a3b8;font-size:0.7rem;">{pct:.0f}%</span></td>'
        p1_3 += f'<td style="font-weight:700;background:#f8fafc;">{total_g}</td></tr>\n'
    # 기타
    etc_g = [g for g in all_genres if g not in top_g]
    etc_by_y = {y: sum(yearly[y]['genre'][g] for g in etc_g) for y in YEARS}
    p1_3 += f'<tr><td class="left" style="color:#94a3b8;">기타 ({len(etc_g)}개)</td>'
    for y in YEARS:
        v = etc_by_y[y]; t = yearly[y]['total']
        pct = v/t*100 if t else 0
        p1_3 += f'<td>{v}<br><span style="color:#cbd5e1;font-size:0.7rem;">{pct:.0f}%</span></td>'
    p1_3 += f'<td>{sum(etc_by_y.values())}</td></tr>\n</table>\n'

    # ==== PART 2: 생존 ====
    # 2-1 전체 생존율
    p2_1 = '<h3>2-1. 전체 3개월 생존율</h3>\n<table>\n<tr><th>연도</th><th>진입 (측정가능)</th><th>생존</th><th>생존율</th></tr>\n'
    for y in YEARS:
        if y == 2026: continue  # 생존 측정 불가
        measurable = [e for e in entries if e['year']==y and e['measurable']]
        survived = [e for e in measurable if e['survived']]
        m_cnt = len(measurable); s_cnt = len(survived)
        rate = s_cnt/m_cnt*100 if m_cnt else 0
        p2_1 += f'<tr><td>{y}</td><td>{m_cnt}</td><td>{s_cnt}</td><td style="color:{color};font-weight:700;">{rate:.1f}%</td></tr>\n'
    # 전체 (22~25)
    meas_all = [e for e in entries if e['year']<=2025 and e['measurable']]
    surv_all = [e for e in meas_all if e['survived']]
    rate_all = len(surv_all)/len(meas_all)*100 if meas_all else 0
    p2_1 += f'<tr class="highlight"><td><strong>전체 (22~25)</strong></td><td><strong>{len(meas_all)}</strong></td><td><strong>{len(surv_all)}</strong></td><td style="color:{color};font-weight:800;">{rate_all:.1f}%</td></tr>\n</table>\n'

    # 2-2 퍼블리셔 그룹별 생존율
    p2_2 = '<h3>2-2. 퍼블리셔 그룹별 3개월 생존율</h3>\n<table>\n<tr><th>퍼블 국적</th><th>진입</th><th>생존</th><th>생존율</th></tr>\n'
    for g in PG_ORDER:
        meas_g = [e for e in meas_all if e['grp']==g]
        surv_g = [e for e in meas_g if e['survived']]
        if not meas_g: continue
        rate = len(surv_g)/len(meas_g)*100
        p2_2 += f'<tr><td class="left" style="color:{PG_COLOR[g]};font-weight:700;">{g}</td><td>{len(meas_g)}</td><td>{len(surv_g)}</td><td style="font-weight:700;color:{PG_COLOR[g]};">{rate:.1f}%</td></tr>\n'
    p2_2 += '</table>\n'

    # 2-3 장르별 3개월 생존율
    genre_entries = defaultdict(list)
    for e in meas_all: genre_entries[e['genre']].append(e)
    p2_3 = '<h3>2-3. 장르별 3개월 생존율</h3>\n<table>\n<tr><th>장르</th><th>진입</th><th>생존</th><th>생존율</th></tr>\n'
    sorted_genres = sorted(genre_entries.items(), key=lambda x:-len(x[1]))
    for g, es in sorted_genres:
        if len(es) < 3: continue  # 표본 너무 작은 건 생략
        surv = [e for e in es if e['survived']]
        rate = len(surv)/len(es)*100
        p2_3 += f'<tr><td class="left"><strong>{g}</strong></td><td>{len(es)}</td><td>{len(surv)}</td><td>{rate:.1f}%</td></tr>\n'
    p2_3 += '</table>\n'

    # ==== PART 3: 요약 ====
    # 전(22~24) vs 후(25만, 26.1Q 제외)
    before = [e for e in entries if 2022<=e['year']<=2024]
    after = [e for e in entries if e['year']==2025]
    b_meas = [e for e in before if e['measurable']]
    b_surv = [e for e in b_meas if e['survived']]
    a_meas = [e for e in after if e['measurable']]
    a_surv = [e for e in a_meas if e['survived']]
    b_rate = len(b_surv)/len(b_meas)*100 if b_meas else 0
    a_rate = len(a_surv)/len(a_meas)*100 if a_meas else 0
    b_monthly = len(before) / (11*3)
    a_monthly = len(after) / 11

    p3 = f'''<h3>3. 요약 — 물량 vs 성적</h3>
<table>
<tr><th>구분</th><th>22~24년 (전)</th><th>2025년 (후)</th><th>변화</th></tr>
<tr><td class="left"><strong>총 신규 진입</strong></td><td>{len(before)}개</td><td>{len(after)}개</td><td class="{'up' if len(after)>len(before)/3 else 'down'}">{len(after)-len(before)/3:+.0f} vs 연평균</td></tr>
<tr><td class="left"><strong>월평균 신규 진입</strong></td><td>{b_monthly:.1f}개/월</td><td>{a_monthly:.1f}개/월</td><td class="{'up' if a_monthly>b_monthly else 'down'}">{a_monthly-b_monthly:+.1f}</td></tr>
<tr><td class="left"><strong>3개월 생존율</strong></td><td>{b_rate:.1f}%</td><td>{a_rate:.1f}%</td><td class="{'up' if a_rate>b_rate else 'down'}">{a_rate-b_rate:+.1f}%p</td></tr>
</table>
<p class="note">※ 2026.1Q는 3개월 생존 측정 기간 부족(+3개월 필요)으로 생존율 계산 대상에서 제외</p>'''

    # 조립
    active_cls = ' active' if is_active else ''
    return f'''<div class="tab-panel{active_cls}" id="tab-{cc.lower()}">
  <div class="panel-title" style="color:{color};background:linear-gradient(90deg,{color_light},transparent);border-left:4px solid {color};">
    {flag} {cc} {cname} 시장 — 신규 진입 & 3개월 생존 분석
  </div>

  <div class="section">
    <h2>1. 신규 진입 물량</h2>
    <p class="desc">연도별 순수 신규 진입 수 (재진입 제외, 1월 제외)</p>
    {p1_1}
    {p1_2}
    {p1_3}
  </div>

  <div class="section">
    <h2>2. 3개월 생존율</h2>
    <p class="desc">진입월 + 3개월 후에도 TOP100 잔류한 비율</p>
    {p2_1}
    {p2_2}
    {p2_3}
  </div>

  <div class="section">
    <h2>3. 요약</h2>
    {p3}
  </div>
</div>'''

# 탭 바 + 패널
tabs = '<div class="tab-bar">'
for i, (cc, flag, cname, color, _) in enumerate(COUNTRIES):
    active = ' active' if i == 0 else ''
    total = len(data[cc])
    tabs += f'<button class="tab-btn{active}" data-target="tab-{cc.lower()}" onclick="switchTab(\'tab-{cc.lower()}\')" style="--tab-color:{color};">'
    tabs += f'<span class="flag">{flag}</span><span>{cc} {cname}</span><span class="badge" style="background:{color};">{total}</span></button>'
tabs += '</div>'

panels = ''.join(build_panel(cc, flag, cname, color, cl, i==0)
                 for i, (cc, flag, cname, color, cl) in enumerate(COUNTRIES))

html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>3국 매출 TOP100 — 신규 진입 & 3개월 생존 분석</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',-apple-system,sans-serif; background:#f5f7fa; color:#333; padding:40px 20px; }}
.container {{ max-width:1100px; margin:0 auto; }}
h1 {{ font-size:1.6rem; margin-bottom:8px; color:#1a1a2e; }}
.subtitle {{ font-size:0.85rem; color:#666; margin-bottom:24px; line-height:1.6; }}
.tab-bar {{ display:flex; gap:8px; margin-bottom:20px; background:#fff; padding:6px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }}
.tab-btn {{ flex:1; padding:14px 16px; border:none; background:#f8f9fb; border-radius:8px; cursor:pointer; font-family:inherit; font-size:0.9rem; font-weight:700; color:#64748b; display:flex; align-items:center; gap:10px; transition:all 0.2s; border-bottom:3px solid transparent; }}
.tab-btn:hover {{ background:#f1f5f9; }}
.tab-btn.active {{ background:#fff; border-bottom-color:var(--tab-color); color:#1a1a2e; }}
.tab-btn .flag {{ font-size:1.3rem; }}
.tab-btn .badge {{ margin-left:auto; color:#fff; padding:2px 10px; border-radius:10px; font-size:0.75rem; font-weight:700; }}
.tab-panel {{ display:none; }}
.tab-panel.active {{ display:block; }}
.panel-title {{ padding:14px 18px; border-radius:6px; margin-bottom:16px; font-size:1.15rem; font-weight:800; }}
.section {{ background:#fff; border-radius:12px; padding:28px 32px; margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }}
.section h2 {{ font-size:1.15rem; color:#1a1a2e; margin-bottom:6px; }}
.section h3 {{ font-size:0.95rem; color:#444; margin:18px 0 10px; }}
.section .desc {{ font-size:0.8rem; color:#888; margin-bottom:16px; }}
table {{ width:100%; border-collapse:collapse; font-size:0.85rem; margin-bottom:12px; }}
th, td {{ padding:8px 12px; text-align:center; border-bottom:1px solid #eee; }}
th {{ background:#f8f9fb; font-weight:600; color:#555; }}
tr:hover {{ background:#f8fbff; }}
td.left {{ text-align:left; }}
.highlight {{ background:#fff3cd !important; }}
.down {{ color:#dc3545; font-weight:600; }}
.up {{ color:#28a745; font-weight:600; }}
.note {{ font-size:0.75rem; color:#999; margin-top:8px; }}
</style>
</head>
<body>
<div class="container">

<h1>3국 매출 TOP100 — 신규 진입 & 3개월 생존 분석</h1>
<p class="subtitle">
기준: <code>dw_app_monthly.in_revenue_top100_unified_os = true</code>, iOS+Android 합산<br>
신규 진입 정의: 전체 기간(2022.01~2026.03) 중 최초 TOP100 진입월 (1월 제외, 재진입 미카운트)<br>
3개월 생존: 진입월 + 3개월 시점에 TOP100 잔류 여부<br>
※ 2026.1Q는 생존 측정 기간 부족으로 생존율 계산에서 제외
</p>

{tabs}

{panels}

<div style="text-align:center;color:#999;font-size:0.75rem;margin-top:24px;padding-top:16px;border-top:1px solid #e8ecf2;">
출처: dw_app_monthly · Sensor Tower · 퍼블 국적 분류: NEXON→KR, FUNFLY→중화권 강제
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
