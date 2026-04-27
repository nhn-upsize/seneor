# -*- coding: utf-8 -*-
"""웹보드 Step 1 스파크라인을 최신 DB 값으로 재생성"""
import re, psycopg2

WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"
MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

# MAU / DL 조회
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, SUM(mau) AS mau_sum, SUM(units) AS u
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY yr, date
)
SELECT yr,
  ROUND((AVG(mau_sum)/10000.0)::numeric, 0) AS mau_man,
  ROUND((AVG(u)/10000.0)::numeric, 1) AS dl_man
FROM base GROUP BY yr ORDER BY yr
""")
data = {}
for yr, mau, dl in cur.fetchall():
    data[yr] = {'mau': int(mau), 'dl': float(dl)}

mau_values = [data[y]['mau'] for y in YEARS]
dl_values = [data[y]['dl'] for y in YEARS]
print(f"MAU: {mau_values}")
print(f"DL:  {dl_values}")

# 스파크라인 SVG 생성
def spark_points(values):
    xs = [20, 85, 150, 215, 280]
    vmax, vmin = max(values), min(values)
    span = vmax - vmin if vmax != vmin else 1
    ys = [round(15 + 45 * (vmax - v) / span, 1) for v in values]
    return list(zip(xs, ys))

def make_spark(gid, color, values, years=YEARS):
    pts = spark_points(values)
    poly = " ".join(f"{x},{y}" for x,y in pts) + " 280,68 20,68"
    line = " ".join(f"{x},{y}" for x,y in pts)
    circles = ""
    for i,(x,y) in enumerate(pts):
        if i == len(pts)-1:
            circles += f'<circle cx="{x}" cy="{y}" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>'
        else:
            circles += f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>'
    labels = ""
    for i,(x,_) in enumerate(pts):
        col, wt = ('#f59e0b','800') if i==len(pts)-1 else ('#64748b','600')
        yr_lbl = years[i] if years[i]=='26.1Q' else f"'{years[i][-2:]}"
        labels += (f'<text x="{x}" y="78" text-anchor="middle" '
                   f'style="font-size:11px;fill:{col};font-weight:{wt};'
                   f'font-family:Pretendard,-apple-system,sans-serif;">{yr_lbl}</text>')
    value_labels = ""
    for i, ((x,y), v) in enumerate(zip(pts, values)):
        c = '#f59e0b' if i==len(pts)-1 else color
        value_labels += (f'<text x="{x}" y="{y-7}" text-anchor="middle" '
                         f'style="font-size:9.5px;fill:{c};font-weight:700;'
                         f'font-family:Pretendard,-apple-system,sans-serif;">{v}</text>')
    return (f'<svg viewBox="0 0 300 85" style="width:100%;max-width:420px;height:68px;margin-top:6px;" preserveAspectRatio="none">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{color}" stop-opacity="0.4"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            f'<polygon fill="url(#{gid})" points="{poly}"/>'
            f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{line}"/>'
            f'{circles}{value_labels}{labels}</svg>')

mau_svg = make_spark("wb-mau-grad", "#f59e0b", mau_values)
dl_svg = make_spark("wb-dl-grad", "#3b82f6", dl_values)

spark_block = (
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;">'
    '<div>'
    '<div style="font-size:0.72rem;color:#64748b;font-weight:600;padding:4px 8px;border-left:2px solid #f59e0b;">'
    '📉 월평균 MAU 추이 (만명) — 활성 유저</div>'
    f'{mau_svg}</div>'
    '<div>'
    '<div style="font-size:0.72rem;color:#64748b;font-weight:600;padding:4px 8px;border-left:2px solid #3b82f6;">'
    '📥 월평균 다운로드 추이 (만건) — 신규 유입</div>'
    f'{dl_svg}</div>'
    '</div>'
)

# 해석 문구 업데이트
new_ins = (f'<div class="ins"><strong>해석:</strong> 웹보드는 <strong>대한민국 모바일 게임 시장 전체 '
           f'ARPMAU(13,263원) 보다도 높은 16,000원대</strong> — 평균 유저당 과금이 시장 평균 대비 '
           f'<strong>1.2배</strong>. <strong>"적은 수의 고과금 충성 유저가 시장을 유지"</strong>하는 구조. '
           f'26.1Q MAU 반등({data["26.1Q"]["mau"]}만)은 신규 Zempot WPL 등 유입 효과로 추정.</div>')

# HTML 패치
def patch(h):
    # 기존 spark 블록 교체
    spark_re = re.compile(
        r'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;">.*?</div></div>',
        re.DOTALL
    )
    m = spark_re.search(h)
    if m:
        h = h[:m.start()] + spark_block + h[m.end():]
    # .ins 해석 교체
    ins_re = re.compile(
        r'<div class="ins"><strong>해석:</strong> 웹보드는.*?유입 효과로 추정\.</div>',
        re.DOTALL
    )
    m2 = ins_re.search(h)
    if m2:
        h = h[:m2.start()] + new_ins + h[m2.end():]
    return h

for path in [WB, MAIN]:
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    o = h.count('<div'); oc = h.count('</div>')
    h = patch(h)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    import os
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")

cur.close(); conn.close()
