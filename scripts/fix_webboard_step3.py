# -*- coding: utf-8 -*-
"""
Step 3 퍼블리셔별 테이블 재계산 + .ins 문구 수정
- 월평균 매출 = SUM(revenue) / 해당연도 전체 월수 (등장한 월만 X)
- 점유율 = 퍼블리셔매출 / 전체합계 (합=100%)
- 25년 전후 변화: 전(22~24, 36개월) vs 후(25~26.1Q, 15개월) 월평균 비교
- webboard 단독 파일 + 메인 HTML 양쪽 모두 반영
"""
import os, re, psycopg2
from collections import defaultdict

WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"
MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# ============================================================
# 전체 월 리스트 (해당 연도 전체 월수 확보)
# ============================================================
cur.execute("""
SELECT
    CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
    COUNT(DISTINCT date) AS n_months
FROM dw_app_monthly
WHERE country='KR' AND genre IN ('Card','Casino','Board')
  AND date BETWEEN '2022-01-01' AND '2026-03-01'
GROUP BY yr ORDER BY yr;
""")
yr_months = dict(cur.fetchall())
print("[연도별 월수]", yr_months)

# ============================================================
# 퍼블리셔 그룹별 매출합 (등장 월만)
# ============================================================
cur.execute("""
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date,
        CASE
            WHEN publisher_name ILIKE '%NHN%' THEN 'NHN'
            WHEN publisher_name ILIKE '%NEOWIZ%' THEN '네오위즈'
            WHEN publisher_name ILIKE '%Zempot%' OR publisher_name ILIKE '%ZEMPOT%' THEN 'Zempot'
            ELSE '기타'
        END AS pub_grp,
        unified_app_id, revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
)
SELECT yr, pub_grp,
       SUM(revenue_krw_100) AS rev_sum,
       COUNT(DISTINCT unified_app_id) AS n_apps
FROM base GROUP BY yr, pub_grp ORDER BY yr, pub_grp;
""")
rows = cur.fetchall()

# 연도 × 퍼블리셔 → (월평균 매출 억, 게임수)
data = defaultdict(dict)
for yr, g, rsum, napps in rows:
    months = yr_months[yr]
    eok = float(rsum) / 1e8 / months if rsum else 0.0
    data[yr][g] = {'eok': eok, 'games': napps}

YEARS = ['2022', '2023', '2024', '2025', '26.1Q']
GROUPS = ['NHN', '네오위즈', 'Zempot', '기타']

print("\n[재계산: 월평균 매출 (억) / 게임수 / 점유율 %]")
print(f"{'YR':<8}{'NHN':>20}{'네오위즈':>20}{'Zempot':>20}{'기타':>20}{'합계':>10}")
for yr in YEARS:
    total = sum(data[yr].get(g, {}).get('eok', 0) for g in GROUPS)
    parts = []
    for g in GROUPS:
        v = data[yr].get(g, {}).get('eok', 0)
        n = data[yr].get(g, {}).get('games', 0)
        share = v/total*100 if total > 0 else 0
        parts.append(f"{v:.1f}억/{share:.1f}%/{n}게임")
    print(f"{yr:<8}" + "".join(f"{s:>20}" for s in parts) + f"{total:>10.1f}억")

# 25년 전후 변화: 전(22~24) 후(25~26.1Q) — 전체 월수 기준
# 전: (22+23+24 매출합) / 36개월, 후: (25+26.1Q) / 15개월
def pub_avg(grp, years, months):
    tot_rev = 0
    for y in years:
        d = data[y].get(grp, {})
        eok = d.get('eok', 0)
        # eok는 "월평균" 이미 나눠져있음 → 실제 합으로 역산
        tot_rev += eok * yr_months[y]
    return tot_rev / months if months > 0 else 0

before_m = sum(yr_months[y] for y in ['2022','2023','2024'])  # 36
after_m = sum(yr_months[y] for y in ['2025','26.1Q'])         # 15
print(f"\n[전후기간 월수] 전={before_m}, 후={after_m}")

change = {}
for g in GROUPS:
    b = pub_avg(g, ['2022','2023','2024'], before_m)
    a = pub_avg(g, ['2025','26.1Q'], after_m)
    diff = a - b
    pct = (diff/b*100) if b else None
    change[g] = (b, a, diff, pct)
    print(f"  {g:<10} 전 {b:.1f}억 → 후 {a:.1f}억  (Δ{diff:+.1f}억, {pct:+.1f}%)" if pct is not None else
          f"  {g:<10} 전 {b:.1f}억 → 후 {a:.1f}억  (Δ{diff:+.1f}억)")

# 합계 행
b_tot = sum(pub_avg(g, ['2022','2023','2024'], before_m) for g in GROUPS)
a_tot = sum(pub_avg(g, ['2025','26.1Q'], after_m) for g in GROUPS)
change['합계'] = (b_tot, a_tot, a_tot-b_tot, (a_tot-b_tot)/b_tot*100)

cur.close(); conn.close()

# ============================================================
# 테이블 HTML 재생성
# ============================================================
def fmt(v, unit='억'):
    return f"{round(v)}{unit}"

def _cls(before, now):
    if before is None or now is None: return ""
    if now > before + 0.5: return " up"
    if now < before - 0.5: return " dn"
    return ""

def build_row(grp, label, row_cls=""):
    tds = []
    prev = None
    for yr in YEARS:
        d = data[yr].get(grp, {})
        v = d.get('eok', 0)
        n = d.get('games', 0)
        total_yr = sum(data[yr].get(g, {}).get('eok', 0) for g in GROUPS)
        share = v/total_yr*100 if total_yr>0 else 0
        is_26 = (yr == '26.1Q')
        td_base = 'num col26' if is_26 else 'num'
        cls = _cls(prev, v)
        prev = v
        if v == 0 and grp == 'Zempot' and yr in ('2023','2024'):
            # 미진입 년도 표시
            tds.append(f'<td class="{td_base}">-<br><span style="color:#64748b;font-size:0.68rem;">-</span></td>')
        else:
            tds.append(
                f'<td class="{td_base}{cls}">{fmt(v)}<br>'
                f'<span style="color:#64748b;font-size:0.68rem;">{share:.1f}%</span><br>'
                f'<span style="color:#cbd5e1;font-size:0.65rem;">{n}게임</span></td>'
            )
    b, a, diff, pct = change[grp]
    change_cls = 'up' if diff > 0.5 else ('dn' if diff < -0.5 else '')
    pct_str = f"{pct:+.0f}%" if pct is not None else "-"
    # 특별 강조(Zempot +700%)
    strong_pct = ''
    if pct and pct >= 200:
        strong_pct = f'<span style="color:#059669;font-weight:700;">{pct_str}</span>'
    else:
        strong_pct = pct_str
    change_td = (
        f'<td class="num {change_cls}"><strong>{round(b)} → {round(a)}</strong><br>'
        f'{diff:+.0f}억 ({strong_pct})</td>'
    )
    return f'        <tr{row_cls}><td>{label}</td>' + ''.join(tds) + change_td + '</tr>'

# 각 행
rows_html = []
rows_html.append(build_row('NHN', '<span class="nhn">NHN</span>', ' class="nhn-row"'))
rows_html.append(build_row('네오위즈', '네오위즈 (피망)'))
rows_html.append(build_row('Zempot', 'Zempot (WPL)'))
rows_html.append(build_row('기타', '기타 (Konami 등)'))

# 합계 행 (점유율 표시 안 함)
tot_tds = []
for yr in YEARS:
    total_yr = sum(data[yr].get(g, {}).get('eok', 0) for g in GROUPS)
    is_26 = (yr == '26.1Q')
    td_base = 'num col26' if is_26 else 'num'
    tot_tds.append(f'<td class="{td_base}">{fmt(total_yr)}</td>')
b, a, diff, pct = change['합계']
tot_change = (
    f'<td class="num up"><strong>{round(b)} → {round(a)}</strong><br>'
    f'{diff:+.0f}억 ({pct:+.0f}%)</td>'
)
rows_html.append(f'        <tr class="tot"><td>합계</td>' + ''.join(tot_tds) + tot_change + '</tr>')

new_tbody = '<tbody>\n' + '\n'.join(rows_html) + '\n      </tbody>'

# ============================================================
# 기존 Step 3 tbody 교체 (양쪽 파일 모두)
# ============================================================
# Step 3 tbody 매칭: <tbody>...<tr class="tot"><td>합계</td>... </tbody>
STEP3_TBODY_RE = re.compile(
    r'<tbody>\s*\n'
    r'        <tr class="nhn-row"><td class="nhn">NHN</td>.*?'
    r'<tr class="tot"><td>합계</td>.*?</tbody>',
    re.DOTALL
)

# Step 3 .ins 교체
OLD_INS = ('<div class="ins"><strong>핵심:</strong> <strong class="nhn">NHN 점유율 63% → 79%까지 상승</strong>한 후 26.1Q는 68.7%로 조정 (Zempot WPL 부상 효과). '
           '네오위즈는 30억 정체 (-6%), 피망 브랜드가 시장에서 힘을 잃는 상황. '
           '<strong>Zempot WPL이 +700% 폭발 성장</strong>하며 신흥 3위로 진입 — NHN에게 장기적 위협 가능성.</div>')
NEW_INS = ('<div class="ins"><strong>핵심:</strong> <strong class="nhn">NHN 점유율 \'22 63% → \'25 79% 피크 → \'26.1Q 68.7%로 조정</strong> '
           '(Zempot WPL 부상 효과). 네오위즈는 15~24% 점유율이 매년 축소, 26.1Q 15%로 최저 '
           '(피망 브랜드 영향력 약화). <strong>Zempot WPL +700% 폭발 성장</strong>하며 신흥 3위 진입, '
           '26.1Q 기준 네오위즈와 점유율 격차 6%p로 좁힘 — NHN·네오위즈 양강 구도에 균열.</div>')

def patch(html):
    # tbody 교체
    m = STEP3_TBODY_RE.search(html)
    if not m:
        raise RuntimeError("Step 3 tbody 매칭 실패")
    html = html[:m.start()] + new_tbody + html[m.end():]
    # .ins 교체
    if OLD_INS in html:
        html = html.replace(OLD_INS, NEW_INS, 1)
    else:
        # 이미 다른 문구로 변경된 경우 스킵 — 경고만
        print("  (경고) 기존 .ins 문구 못찾음, 스킵")
    return html

for path in [WB, MAIN]:
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_step3fix'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o_open, o_close = h.count('<div'), h.count('</div>')
    h = patch(h)
    n_open, n_close = h.count('<div'), h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    ok = '✅' if n_open == n_close else '❌'
    print(f"\n[{os.path.basename(path)}] <div> {o_open}→{n_open}, </div> {o_close}→{n_close}  {ok}")
