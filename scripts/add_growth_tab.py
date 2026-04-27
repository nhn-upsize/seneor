#!/usr/bin/env python3
"""Add growth_games_ad_age tab to NHN_market_analysis.html"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# Data per country - sorted by delta desc, grouped by pub_group
KR = [
    # KR pub
    ('kr','KR','MapleStory : Idle RPG','RPG','비MMORPG',61.8,30.1,0.0,533.8,533.8),
    ('kr','KR','뱀피르','RPG','MMORPG',None,None,0.0,234.1,234.1),
    ('kr','KR','마비노기 모바일','RPG','MMORPG',27.7,29.3,0.0,169.5,169.5),
    ('kr','KR','Seven Knights Re:BIRTH','RPG','비MMORPG',29.6,27.7,0.0,166.1,166.1),
    ('kr','KR','StoneAge: Idle Adventure','RPG','비MMORPG',32.3,32.0,0.0,148.6,148.6),
    ('kr','KR','RF 온라인 넥스트','RPG','MMORPG',33.5,34.9,0.0,107.1,107.1),
    ('kr','KR','AION2','RPG','MMORPG',22.7,34.6,0.0,61.3,61.3),
    ('kr','KR','레전드 오브 이미르','RPG','MMORPG',17.0,34.8,0.0,55.1,55.1),
    # 중화권
    ('cn','중화권','Whiteout Survival','Strategy',None,80.3,34.2,159.8,353.6,193.8),
    ('cn','중화권','Kingshot','Strategy',None,75.1,34.3,0.0,107.4,107.4),
    ('cn','중화권','Last Z: Survival Shooter','Strategy',None,65.3,35.9,0.0,89.4,89.4),
    ('cn','중화권','I9: 인페르노 나인','RPG','MMORPG',53.9,34.2,0.0,62.0,62.0),
    ('cn','중화권','Dark War:Survival','Strategy',None,69.2,34.5,0.0,52.7,52.7),
    # 기타
    ('etc','기타','Royal Match','Puzzle',None,45.2,38.3,65.7,117.6,51.9),
]

JP = [
    # JP pub
    ('jp','JP','SD Gundam G Gen ETERNAL','Strategy',None,24.9,34.0,0.0,287.6,287.6),
    ('jp','JP','Shadowverse: Worlds Beyond','Card',None,14.7,27.5,0.0,131.9,131.9),
    ('jp','JP','eFootball™','Sports',None,9.4,30.0,157.2,233.7,76.5),
    ('jp','JP','キングダム 覇道','Strategy',None,None,None,0.0,73.6,73.6),
    ('jp','JP','魔法少女まどかマギカ Magia Exedra','RPG','비MMORPG',22.7,31.8,0.0,61.6,61.6),
    ('jp','JP','KAIJU NO. 8 THE GAME','RPG','비MMORPG',18.7,31.7,0.0,58.6,58.6),
    ('jp','JP','P5X ペルソナ５','RPG','비MMORPG',35.9,30.0,0.0,50.8,50.8),
    # 중화권
    ('cn','중화권','Whiteout Survival','Strategy',None,74.1,36.4,110.7,279.8,169.1),
    ('cn','중화권','Last War:Survival Game','Strategy',None,46.6,37.3,296.4,462.6,166.2),
    ('cn','중화권','Arknights: Endfield','RPG','비MMORPG',39.1,27.5,0.0,119.3,119.3),
    ('cn','중화권','信長の野望 真戦','Strategy',None,None,None,0.0,84.1,84.1),
    ('cn','중화권','Kingshot','Strategy',None,76.1,34.9,0.0,83.8,83.8),
    ('cn','중화권','Last Z: Survival Shooter','Strategy',None,71.0,37.4,0.0,80.9,80.9),
    ('cn','중화권','Gossip Harbor: Merge & Story','Puzzle',None,83.4,37.7,39.2,98.0,58.8),
    # 기타
    ('etc','기타','Royal Match','Puzzle',None,35.3,41.5,106.0,156.4,50.5),
]

US = [
    # 중화권 (가장 많음)
    ('cn','중화권','Kingshot','Strategy',None,73.9,33.9,0.0,521.4,521.4),
    ('cn','중화권','Last War:Survival Game','Strategy',None,54.9,37.0,630.4,1109.7,479.3),
    ('cn','중화권','Gossip Harbor: Merge & Story','Puzzle',None,85.1,33.1,93.2,456.9,363.6),
    ('cn','중화권','Last Z: Survival Shooter','Strategy',None,68.7,36.1,0.0,256.6,256.6),
    ('cn','중화권','Whiteout Survival','Strategy',None,79.2,32.1,401.8,583.1,181.3),
    ('cn','중화권','Destiny: Rising','Action',None,32.3,30.5,0.0,152.3,152.3),
    ('cn','중화권','Tasty Travels: Merge Game','Puzzle',None,71.1,36.6,0.0,109.5,109.5),
    ('cn','중화권','Dark War:Survival','Strategy',None,73.2,34.8,55.0,148.0,93.0),
    ('cn','중화권','Archero 2','Action',None,46.7,29.7,0.0,78.5,78.5),
    ('cn','중화권','Etheria: Restart','RPG','비MMORPG',26.2,28.0,0.0,70.1,70.1),
    ('cn','중화권','Top Heroes: Kingdom Saga','Strategy',None,70.9,33.8,56.8,124.2,67.5),
    ('cn','중화권','Love and Deepspace','Simulation',None,20.9,27.1,63.1,113.1,50.0),
    # 기타
    ('etc','기타','Royal Match','Puzzle',None,56.0,41.1,910.6,1199.3,288.7),
    ('etc','기타','Royal Kingdom','Puzzle',None,74.6,41.7,78.7,362.9,284.2),
    ('etc','기타','Clash Royale','Strategy',None,10.1,27.8,145.8,392.2,246.4),
    ('etc','기타','Pixel Flow!','Puzzle',None,83.3,32.0,0.0,205.1,205.1),
    ('etc','기타','Free Fire: Undersea Mystery','Adventure',None,6.9,28.2,178.9,368.9,190.0),
    ('etc','기타','Disney Solitaire','Card',None,47.7,35.0,0.0,142.9,142.9),
    ('etc','기타','Township','Puzzle',None,58.1,36.7,329.9,463.8,134.0),
    ('etc','기타','Color Block Jam','Puzzle',None,80.8,37.2,0.0,124.1,124.1),
    ('etc','기타','All in Hole','Puzzle',None,76.0,37.9,0.0,102.0,102.0),
    ('etc','기타','Toon Blast','Arcade',None,53.5,41.6,215.2,302.2,87.0),
    # 북미
    ('na','북미','Magic: The Gathering Arena','Strategy',None,9.7,30.3,0.0,61.5,61.5),
    # JP
    ('jp','JP','Umamusume: Pretty Derby','Adventure',None,21.8,26.4,0.0,142.2,142.2),
    # KR
    ('kr','KR','MapleStory : Idle RPG','RPG','비MMORPG',67.9,29.0,0.0,130.9,130.9),
]

def fmt_paid(p):
    if p is None:
        return '<td class="tg-r" style="color:#94a3b8;">N/A</td>'
    if p >= 50:
        cls = 'high'
    elif p >= 25:
        cls = 'mid'
    else:
        cls = 'low'
    return f'<td class="tg-r"><div class="tg-paid-bar"><div class="tg-bar-track"><div class="tg-bar-fill {cls}" style="width:{min(p,100)}%"></div></div><span class="tg-bar-val {cls}">{p:.1f}</span></div></td>'

def fmt_age(a):
    if a is None:
        return '<td class="tg-r" style="color:#94a3b8;">N/A</td>'
    cls = ' tg-age-old' if a >= 38 else ''
    return f'<td class="tg-r{cls}">{a:.1f}</td>'

def fmt_pre(v, is_new):
    if is_new or v == 0:
        return '<td class="tg-r"><span class="tg-new-tag">신작</span></td>'
    return f'<td class="tg-r">{v:,.1f}</td>'

PUB_TAG_CLS = {'kr':'tg-pub-kr','jp':'tg-pub-jp','cn':'tg-pub-cn','na':'tg-pub-na','etc':'tg-pub-etc'}

def gen_rows(games):
    rows = []
    prev_pg = None
    for g in games:
        pg, pg_label, name, genre, sub, paid, age, pre, post, delta = g
        is_new = (pre == 0.0)
        sub_html = f'<span class="tg-sub-genre">{sub}</span>' if sub else ''
        # First row in each pub group gets the tag, others get blank
        if pg != prev_pg:
            tag_cell = f'<td><span class="tg-pub-tag {PUB_TAG_CLS[pg]}">{pg_label}</span></td>'
            border_top = ' style="border-top:2px solid #e2e8f0;"' if prev_pg is not None else ''
            prev_pg = pg
        else:
            tag_cell = '<td></td>'
            border_top = ''
        rows.append(f'''        <tr{border_top}>
          {tag_cell}
          <td class="tg-name">{name}</td>
          <td><span class="tg-genre-tag">{genre}</span>{sub_html}</td>
          {fmt_paid(paid)}
          {fmt_age(age)}
          {fmt_pre(pre, is_new)}
          <td class="tg-r">{post:,.1f}</td>
          <td class="tg-r tg-change-up">+{delta:,.1f}</td>
        </tr>''')
    return '\n'.join(rows)

CSS = '''
  /* ===== Tab 3: Growth Games (광고/연령) ===== */
  .tab-growth { padding: 40px 24px; background:#e8ecf1; }
  .tab-growth .tg-container { max-width:1200px; margin:0 auto; display:flex; flex-direction:column; gap:24px; }
  .tab-growth .tg-header { text-align:center; }
  .tab-growth .tg-header h1 { font-size:1.4rem; font-weight:900; margin-bottom:6px; }
  .tab-growth .tg-header .tg-sub { font-size:0.72rem; color:#475569; line-height:1.6; }
  .tab-growth .tg-card { background:#fff; border-radius:10px; box-shadow:0 4px 20px rgba(0,0,0,0.06); padding:24px 28px; position:relative; overflow:hidden; }
  .tab-growth .tg-card::before { content:''; position:absolute; top:0; left:0; right:0; height:4px; border-radius:10px 10px 0 0; }
  .tab-growth .tg-card.tg-kr::before { background:#2563eb; }
  .tab-growth .tg-card.tg-jp::before { background:#dc2626; }
  .tab-growth .tg-card.tg-us::before { background:#7c3aed; }
  .tab-growth .tg-card h2 { font-size:1rem; font-weight:800; margin-bottom:14px; display:flex; align-items:center; gap:8px; }
  .tab-growth .tg-card h2 .tg-flag { font-size:1.2rem; }
  .tab-growth table { width:100%; border-collapse:collapse; font-size:0.72rem; }
  .tab-growth th { background:#f1f5f9; padding:8px 10px; text-align:left; font-weight:700; border-bottom:2px solid #e2e8f0; white-space:nowrap; color:#475569; }
  .tab-growth th.tg-r { text-align:right; }
  .tab-growth td { padding:7px 10px; border-bottom:1px solid #e2e8f0; color:#475569; }
  .tab-growth td.tg-r { text-align:right; font-variant-numeric:tabular-nums; }
  .tab-growth td.tg-name { font-weight:700; color:#1e293b; max-width:200px; }
  .tab-growth .tg-pub-tag { display:inline-block; font-size:0.6rem; font-weight:700; padding:2px 7px; border-radius:6px; color:#fff; }
  .tab-growth .tg-pub-kr { background:#2563eb; }
  .tab-growth .tg-pub-jp { background:#dc2626; }
  .tab-growth .tg-pub-cn { background:#d97706; }
  .tab-growth .tg-pub-na { background:#8b5cf6; }
  .tab-growth .tg-pub-etc { background:#6b7280; }
  .tab-growth .tg-genre-tag { font-size:0.62rem; color:#94a3b8; }
  .tab-growth .tg-sub-genre { font-size:0.58rem; background:#eff6ff; color:#2563eb; padding:1px 5px; border-radius:4px; margin-left:4px; font-weight:600; }
  .tab-growth .tg-paid-bar { display:flex; align-items:center; gap:6px; justify-content:flex-end; }
  .tab-growth .tg-bar-track { width:80px; height:14px; background:#f1f5f9; border-radius:3px; overflow:hidden; flex-shrink:0; }
  .tab-growth .tg-bar-fill { height:100%; border-radius:3px; }
  .tab-growth .tg-bar-fill.high { background:linear-gradient(90deg,#fca5a5,#dc2626); }
  .tab-growth .tg-bar-fill.mid { background:linear-gradient(90deg,#fde68a,#f59e0b); }
  .tab-growth .tg-bar-fill.low { background:linear-gradient(90deg,#a7f3d0,#059669); }
  .tab-growth .tg-bar-val { font-size:0.68rem; font-weight:700; width:32px; text-align:right; flex-shrink:0; }
  .tab-growth .tg-bar-val.high { color:#dc2626; }
  .tab-growth .tg-bar-val.mid { color:#b45309; }
  .tab-growth .tg-bar-val.low { color:#059669; }
  .tab-growth .tg-age-old { color:#b45309; font-weight:700; }
  .tab-growth .tg-new-tag { font-size:0.56rem; background:#ecfdf5; color:#059669; padding:1px 5px; border-radius:4px; font-weight:700; }
  .tab-growth .tg-change-up { color:#059669; font-weight:800; }
  .tab-growth .tg-insight { margin-top:14px; font-size:0.7rem; color:#475569; background:#f8fafc; border-radius:8px; padding:12px 16px; line-height:1.7; border:1px solid #e2e8f0; }
  .tab-growth .tg-insight strong { color:#1e293b; }
  .tab-growth .tg-summary { display:flex; gap:16px; }
  .tab-growth .tg-summary .tg-card { flex:1; padding:18px 22px; }
  .tab-growth .tg-summary .tg-summary-title { font-size:0.78rem; font-weight:800; margin-bottom:8px; }
  .tab-growth .tg-summary .tg-summary-body { font-size:0.68rem; color:#475569; line-height:1.8; }
  .tab-growth .tg-footer { text-align:center; font-size:0.6rem; color:#94a3b8; padding:8px 0; line-height:1.5; }
'''

TAB_HTML = f'''
<!-- ===== TAB 3: 25년 성장 게임 (광고/연령) ===== -->
<div id="tab-growth" class="tab-content">
<div class="tab-growth">
<div class="tg-container">

  <div class="tg-header">
    <h1>25년 이후 성장 게임 — 광고유입 비중 &amp; 유저 연령 패턴</h1>
    <div class="tg-sub">
      매출 TOP 100 (iOS+Android 합산, in_revenue_top100_unified_os = TRUE) | revenue_usd_100p × 연도별 환율 | 변화 50억 이상 성장 앱만<br>
      연도별 환율(22:1,292 / 23:1,307 / 24:1,364 / 25:1,422 / 26:1,409) | 광고유입 = paid_abs/(paid+organic+browser) | 연령 = avg_age_total
    </div>
  </div>

  <!-- Summary boxes -->
  <div class="tg-summary">
    <div class="tg-card">
      <div class="tg-summary-title" style="color:#b45309;">광고유입 패턴</div>
      <div class="tg-summary-body">
        <strong style="color:#d97706;">중화권 Strategy 53~85%</strong> — 3국 모두 일관된 광고 기반 성장<br>
        <strong style="color:#dc2626;">JP 퍼블리셔 9~36%</strong> — IP 파워 + 오가닉 중심<br>
        <strong style="color:#2563eb;">KR 신작 RPG 17~68%</strong> — MapleStory Idle 62%, AION2 23%로 편차 큼<br>
        <strong>Clash Royale 10% / MTG Arena 10%</strong> — IP+업데이트 기반, 광고 무관 성장
      </div>
    </div>
    <div class="tg-card">
      <div class="tg-summary-title" style="color:#2563eb;">유저 연령 패턴</div>
      <div class="tg-summary-body">
        <strong style="color:#b45309;">Puzzle 38~42세</strong> — Royal Match 41세, Triple Match 42세 등 중장년 핵심<br>
        <strong style="color:#d97706;">중화권 Strategy 33~37세</strong> — 30대 중반 타겟 일관됨<br>
        <strong style="color:#2563eb;">KR 신작 RPG 28~35세</strong> — Seven Knights RE:BIRTH 28세로 가장 젊음<br>
        <strong>Umamusume 26세 / Clash Royale 28세</strong> — 가장 젊은 유저층
      </div>
    </div>
  </div>

  <!-- KR -->
  <div class="tg-card tg-kr">
    <h2><span class="tg-flag">&#127472;&#127479;</span> KR 한국</h2>
    <table>
      <thead>
        <tr><th>퍼블 그룹</th><th>앱</th><th>장르</th><th class="tg-r">25년후 광고유입(%)</th><th class="tg-r">평균연령</th><th class="tg-r">25년전(억)</th><th class="tg-r">25년후(억)</th><th class="tg-r">변화(억)</th></tr>
      </thead>
      <tbody>
{gen_rows(KR)}
      </tbody>
    </table>
    <div class="tg-insight">
      <strong>KR 퍼블리셔 신작 8종 모두 RPG</strong> — MapleStory Idle(비MMORPG, 광고 62%) + 뱀피르/마비노기/RF/AION2(MMORPG). MMORPG 신작들은 광고 17~34%로 오가닉 중심.<br>
      <strong>중화권 Strategy 3종(Whiteout/Kingshot/Last Z) 모두 광고 65~80%</strong> — 광고 기반 성장 모델 뚜렷. 연령 34~36세.
    </div>
  </div>

  <!-- JP -->
  <div class="tg-card tg-jp">
    <h2><span class="tg-flag">&#127471;&#127477;</span> JP 일본</h2>
    <table>
      <thead>
        <tr><th>퍼블 그룹</th><th>앱</th><th>장르</th><th class="tg-r">25년후 광고유입(%)</th><th class="tg-r">평균연령</th><th class="tg-r">25년전(억)</th><th class="tg-r">25년후(억)</th><th class="tg-r">변화(억)</th></tr>
      </thead>
      <tbody>
{gen_rows(JP)}
      </tbody>
    </table>
    <div class="tg-insight">
      <strong>JP 퍼블리셔는 광고 9~36%</strong> — IP 파워 + 오가닉 중심. SD Gundam(건담 IP), Shadowverse(카드 IP), eFootball(축구 IP), KAIJU NO.8(애니 IP).<br>
      <strong>중화권은 JP에서도 광고 39~83%</strong> — 시장 무관하게 일관된 광고 기반 전략. Last War 47%(낮은 편), Gossip Harbor 83%.
    </div>
  </div>

  <!-- US -->
  <div class="tg-card tg-us">
    <h2><span class="tg-flag">&#127482;&#127480;</span> US 미국</h2>
    <table>
      <thead>
        <tr><th>퍼블 그룹</th><th>앱</th><th>장르</th><th class="tg-r">25년후 광고유입(%)</th><th class="tg-r">평균연령</th><th class="tg-r">25년전(억)</th><th class="tg-r">25년후(억)</th><th class="tg-r">변화(억)</th></tr>
      </thead>
      <tbody>
{gen_rows(US)}
      </tbody>
    </table>
    <div class="tg-insight">
      <strong>US 중화권 Strategy 4종(Kingshot/Last War/Last Z/Whiteout) 합산 +1,438억</strong> — US 성장의 핵심 동력. 광고 55~79%.<br>
      <strong>Puzzle(Royal Match/Royal Kingdom)은 40대 중장년</strong> (41~42세) + 고광고(56~75%). <strong>Clash Royale는 예외</strong> — 광고 10%로 IP/업데이트 기반 리바이벌, 27.8세 젊은 층.
    </div>
  </div>

  <div class="tg-footer">
    NHN 모바일 게임 시장 분석 | Sensor Tower dw_app_monthly | <strong>in_revenue_top100_unified_os = TRUE 기준</strong><br>
    25년전 = 22~24 월평균(앱 존재월) / 25년후 = 25~26.1Q 월평균(앱 존재월) | 광고유입 = paid_abs/(paid+organic+browser), null 제외 | 연령 = avg_age_total
  </div>

</div>
</div>
</div>
'''

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add CSS before </style>
    html = html.replace('</style>', CSS + '</style>', 1)

    # 2. Add tab content before tab-criteria
    marker = '<!-- ===== TAB 3: 데이터 기준 명세 ====='
    if marker not in html:
        # Try alternative marker
        marker = '<div id="tab-criteria"'
    html = html.replace(marker, TAB_HTML + '\n' + marker, 1)

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    # Verify
    d = html.count('<div')
    c = html.count('</div>')
    print(f'div: {d}/{c} diff={d-c}')
    print(f'Size: {len(html):,} bytes')
    print('Done!')

if __name__ == '__main__':
    main()
