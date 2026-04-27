#!/usr/bin/env python3
"""Replace Step 5 game tables + SVG charts with new data"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# ============================================================
# SVG DATA
# ============================================================
SVG_DATA = {
    'KR': {'mau': [4291,4090,3661,3619,3599], 'dl': [569,557,620,549,497]},
    'JP': {'mau': [10158,9588,8647,8716,8466], 'dl': [757,851,802,716,726]},
    'US': {'mau': [30580,29394,29386,29698,30371], 'dl': [2953,3059,3152,3175,3197]},
}
SVG_DATA['ALL'] = {
    'mau': [sum(SVG_DATA[c]['mau'][i] for c in ['KR','JP','US']) for i in range(5)],
    'dl':  [sum(SVG_DATA[c]['dl'][i] for c in ['KR','JP','US']) for i in range(5)],
}

def svg_points(vals):
    """Calculate SVG y-coordinates for sparkline"""
    mn, mx = min(vals), max(vals)
    rng = mx - mn if mx != mn else 1
    xs = [20, 85, 150, 215, 280]
    ys = [round(60 - (v - mn) / rng * 50 + 10, 1) for v in vals]
    return xs, ys

def make_polygon(xs, ys):
    pts = ' '.join(f"{x},{y}" for x,y in zip(xs,ys))
    return f"{pts} 280,68 20,68"

def make_polyline(xs, ys):
    return ' '.join(f"{x},{y}" for x,y in zip(xs,ys))

# ============================================================
# STEP 5 GAME DATA - KR
# ============================================================
KR_ZHCN_UP = [
    ("Whiteout Survival", 0,94,215,381,243, 103,353,"+250"),
    ("Last War:Survival Game", 0,32,332,276,214, 121,264,"+143"),
    ("Kingshot", 0,0,0,99,137, 0,107,"+107"),
    ("Last Z: Survival Shooter", 0,0,0,86,102, 0,89,"+89"),
    ("I9: 인페르노 나인", 0,0,0,70,28, 0,62,"+62"),
]
KR_ZHCN_DN = [
    ("Genshin Impact", 93,93,53,34,35, 80,34,"-46"),
    ("아르케랜드", 105,32,0,0,0, 46,0,"-46"),
    ("히어로즈 테일즈", 85,26,10,0,0, 40,0,"-40"),
]
KR_KR_UP = [
    ("MapleStory : Idle RPG", 0,0,0,604,487, 0,581,"+581"),
    ("뱀피르", 0,0,0,348,44, 0,287,"+287"),
    ("Seven Knights Re:BIRTH", 0,0,0,215,36, 0,179,"+179"),
    ("마비노기 모바일", 0,0,0,197,79, 0,173,"+173"),
]
KR_KR_DN = [
    ("Lineage W", 350,144,106,67,25, 200,59,"-141"),
    ("오딘: 발할라 라이징", 297,237,201,135,73, 245,123,"-122"),
    ("나이트 크로우", 0,244,50,21,12, 98,19,"-79"),
    ("리니지2M", 147,131,98,59,23, 125,52,"-73"),
    ("리니지M", 398,464,497,435,187, 453,385,"-68"),
]
KR_ETC_UP = [("Royal Match", 13,51,129,123,96, 64,118,"+54")]
KR_NA_UP = [("Roblox", 67,70,73,117,91, 70,112,"+42")]

def gen_game_row(name, y22,y23,y24,y25,y26, pre,post, delta, is_tot=False):
    cls = 'tot' if is_tot else ''
    dcls = 'up' if delta.startswith('+') else 'dn'
    y26_cls = 'col26'
    pre_post = f"{pre} → {post}" if not is_tot else "-"
    tr_cls = f' class="{cls}"' if cls else ''
    return f'          <tr{tr_cls}><td>{name}</td><td class="num">{y22}</td><td class="num">{y23}</td><td class="num">{y24}</td><td class="num">{y25}</td><td class="num {y26_cls}">{y26}</td><td class="num">{pre_post}</td><td class="num {dcls}">{delta}억</td></tr>'

def gen_game_table(games, label="합계"):
    rows = []
    for g in games:
        rows.append(gen_game_row(g[0], g[1],g[2],g[3],g[4],g[5], g[6],g[7], g[8]))
    # Total row
    totals = [sum(g[i] for g in games) for i in range(1,6)]
    tot_delta = sum(int(g[8].replace('+','').replace('억','')) for g in games)
    sign = '+' if tot_delta > 0 else ''
    rows.append(gen_game_row(label, totals[0],totals[1],totals[2],totals[3],totals[4], '-','-', f"{sign}{tot_delta}", is_tot=True))
    return '\n'.join(rows)

# ============================================================
# MAIN
# ============================================================
def fix_svg(html, panel_id, metric, old_vals, new_vals, grad_id, color):
    """Fix SVG chart within a specific panel"""
    panel_start = html.find(f'id="{panel_id}"')
    if panel_start == -1:
        return html

    # Find the section after panel_start that contains the old values
    # SVG charts have specific gradient IDs we can search for
    grad_search = f'id="{grad_id}"'
    grad_pos = html.find(grad_search, panel_start)
    if grad_pos == -1:
        print(f"  SKIP SVG: {grad_id} not found in {panel_id}")
        return html

    # Find the enclosing SVG
    svg_start = html.rfind('<svg', panel_start, grad_pos)
    svg_end = html.find('</svg>', grad_pos) + 6
    if svg_start == -1:
        return html

    old_svg = html[svg_start:svg_end]

    # Calculate new points
    xs, ys = svg_points(new_vals)
    new_poly = make_polygon(xs, ys)
    new_line = make_polyline(xs, ys)

    # Replace polygon points
    new_svg = re.sub(r'<polygon fill="[^"]*" points="[^"]*"',
                     f'<polygon fill="url(#{grad_id})" points="{new_poly}"', old_svg)
    # Replace polyline points
    new_svg = re.sub(r'<polyline fill="none" stroke="[^"]*" stroke-width="[^"]*" points="[^"]*"',
                     f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{new_line}"', new_svg)
    # Replace circle positions
    for i in range(5):
        old_circle_pattern = f'cx="{20 if i==0 else 85 if i==1 else 150 if i==2 else 215 if i==3 else 280}"'
        # Update cy values
        pass  # Circle positions are harder to regex reliably

    # Replace circles by finding all circle elements
    circles = list(re.finditer(r'<circle cx="(\d+)" cy="([\d.]+)"', new_svg))
    for i, c in enumerate(circles):
        if i < 5:
            old_cy = c.group(2)
            new_cy = str(ys[i])
            new_svg = new_svg.replace(f'cx="{c.group(1)}" cy="{old_cy}"',
                                       f'cx="{xs[i]}" cy="{new_cy}"', 1)

    # Replace text labels (the number values)
    if metric in ['dl']:
        for i, (old_v, new_v) in enumerate(zip(old_vals, new_vals)):
            old_str = f'>{old_v:,}<' if old_v >= 1000 else f'>{old_v}<'
            new_str = f'>{new_v:,}<' if new_v >= 1000 else f'>{new_v}<'
            if old_str in new_svg:
                new_svg = new_svg.replace(old_str, new_str, 1)

    html = html[:svg_start] + new_svg + html[svg_end:]
    print(f"  OK SVG: {grad_id} in {panel_id}")
    return html

def fix_dl_text(html, panel_id, old_vals, new_vals):
    """Fix DL text description below SVG chart"""
    panel_start = html.find(f'id="{panel_id}"')
    if panel_start == -1:
        return html

    # Old DL text patterns
    old_pre = round(sum(old_vals[:3])/3)
    old_post = round((old_vals[3]*12 + old_vals[4]*3)/15)
    new_pre = round(sum(new_vals[:3])/3)
    new_post = round((new_vals[3]*12 + new_vals[4]*3)/15)

    return html

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # ===== SVG CHARTS =====
    print("=== SVG Charts ===")

    # MAU charts
    mau_grads = {'all': 'all-mau-grad', 'kr': 'kr-mau-grad', 'jp': 'jp-mau-grad', 'us': 'us-mau-grad'}
    mau_colors = {'all': '#64748b', 'kr': '#f59e0b', 'jp': '#f59e0b', 'us': '#f59e0b'}
    old_mau = {
        'all': [43097,41517,40645,39967,38187],
        'kr': [4396,4242,3768,3632,3680],
        'jp': [10114,9493,8484,8582,8456],
        'us': [28587,27783,28394,27753,26050],
    }

    for panel in ['all','kr','jp','us']:
        key = panel.upper()
        html = fix_svg(html, panel, 'mau', old_mau[panel], SVG_DATA[key]['mau'],
                       mau_grads[panel], mau_colors[panel])

    # DL charts
    dl_grads = {'all': 'all-dl-grad', 'kr': 'kr-dl-grad', 'jp': 'jp-dl-grad', 'us': 'us-dl-grad'}
    dl_colors = {'all': '#64748b', 'kr': '#3b82f6', 'jp': '#3b82f6', 'us': '#3b82f6'}
    old_dl = {
        'all': [4338,4570,4680,4503,4454],
        'kr': [600,591,649,568,513],
        'jp': [766,853,815,719,725],
        'us': [2971,3126,3215,3216,3215],
    }

    for panel in ['all','kr','jp','us']:
        key = panel.upper()
        html = fix_svg(html, panel, 'dl', old_dl[panel], SVG_DATA[key]['dl'],
                       dl_grads[panel], dl_colors[panel])

    # Fix DL text labels in SVGs
    for panel in ['kr']:
        for old_v, new_v in zip(old_dl[panel], SVG_DATA[panel.upper()]['dl']):
            html = html.replace(f'>{old_v}<', f'>{new_v}<', 1)

    # Fix DL summary text
    # KR DL text
    html = html.replace('22년 600만건', f'22년 {SVG_DATA["KR"]["dl"][0]}만건')
    html = html.replace('25년 568만건', f'25년 {SVG_DATA["KR"]["dl"][3]}만건')
    html = html.replace('26.1Q 513만건', f'26.1Q {SVG_DATA["KR"]["dl"][4]}만건')
    html = html.replace('전 613만 → 후 557만, -9%',
                         f'전 {round(sum(SVG_DATA["KR"]["dl"][:3])/3)}만 → 후 {round((SVG_DATA["KR"]["dl"][3]*12+SVG_DATA["KR"]["dl"][4]*3)/15)}만, -{round((1-round((SVG_DATA["KR"]["dl"][3]*12+SVG_DATA["KR"]["dl"][4]*3)/15)/round(sum(SVG_DATA["KR"]["dl"][:3])/3))*100)}%')

    # JP DL text
    html = html.replace('22년 766만건', f'22년 {SVG_DATA["JP"]["dl"][0]}만건')
    html = html.replace('25년 719만건', f'25년 {SVG_DATA["JP"]["dl"][3]}만건')
    html = html.replace('26.1Q 725만건', f'26.1Q {SVG_DATA["JP"]["dl"][4]}만건')
    html = html.replace('전 812만 → 후 720만, -11%',
                         f'전 {round(sum(SVG_DATA["JP"]["dl"][:3])/3)}만 → 후 {round((SVG_DATA["JP"]["dl"][3]*12+SVG_DATA["JP"]["dl"][4]*3)/15)}만, -{round((1-round((SVG_DATA["JP"]["dl"][3]*12+SVG_DATA["JP"]["dl"][4]*3)/15)/round(sum(SVG_DATA["JP"]["dl"][:3])/3))*100)}%')

    # ALL DL text
    html = html.replace('22년 4,338만건', f'22년 {SVG_DATA["ALL"]["dl"][0]:,}만건')
    html = html.replace('25년 4,503만건', f'25년 {SVG_DATA["ALL"]["dl"][3]:,}만건')
    html = html.replace('26.1Q 4,454만건', f'26.1Q {SVG_DATA["ALL"]["dl"][4]:,}만건')
    html = html.replace('전 4,529만 → 후 4,493만, -1%',
                         f'전 {round(sum(SVG_DATA["ALL"]["dl"][:3])/3):,}만 → 후 {round((SVG_DATA["ALL"]["dl"][3]*12+SVG_DATA["ALL"]["dl"][4]*3)/15):,}만, {round((round((SVG_DATA["ALL"]["dl"][3]*12+SVG_DATA["ALL"]["dl"][4]*3)/15)/round(sum(SVG_DATA["ALL"]["dl"][:3])/3)-1)*100)}%')

    # ===== STEP 5 GAME TABLES =====
    print("\n=== Step 5 Game Tables ===")

    # KR Step 5 - Replace key game values
    # 중화권 증가 TOP 5
    kr_step5_replacements = [
        # Whiteout old → new
        ('Whiteout Survival</td><td class="num">0</td><td class="num">78</td><td class="num">215</td><td class="num">381</td><td class="num col26">243</td><td class="num">98 → 354</td><td class="num up">+256억',
         'Whiteout Survival</td><td class="num">0</td><td class="num">94</td><td class="num">215</td><td class="num">381</td><td class="num col26">243</td><td class="num">103 → 353</td><td class="num up">+250억'),
        # Last War
        ('Last War:Survival Game</td><td class="num">0</td><td class="num">7</td><td class="num">423</td><td class="num">276</td><td class="num col26">214</td><td class="num">112 → 263</td><td class="num up">+151억',
         'Last War:Survival Game</td><td class="num">0</td><td class="num">32</td><td class="num">332</td><td class="num">276</td><td class="num col26">214</td><td class="num">121 → 264</td><td class="num up">+143억'),
        # Kingshot
        ('Kingshot</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">82</td><td class="num col26">137</td><td class="num">0 → 93</td><td class="num up">+93억',
         'Kingshot</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">99</td><td class="num col26">137</td><td class="num">0 → 107</td><td class="num up">+107억'),
        # Last Z
        ('Last Z: Survival Shooter</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">68</td><td class="num col26">142</td><td class="num">0 → 89</td><td class="num up">+89억',
         'Last Z: Survival Shooter</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">86</td><td class="num col26">102</td><td class="num">0 → 89</td><td class="num up">+89억'),

        # Genshin Impact (중화권 감소)
        ('Genshin Impact</td><td class="num">120</td><td class="num">75</td><td class="num">46</td><td class="num">42</td><td class="num col26">7</td><td class="num">80 → 34</td><td class="num dn">-46억',
         'Genshin Impact</td><td class="num">93</td><td class="num">93</td><td class="num">53</td><td class="num">34</td><td class="num col26">35</td><td class="num">80 → 34</td><td class="num dn">-46억'),
        # 히어로즈 테일즈
        ('히어로즈 테일즈</td><td class="num">15</td><td class="num">62</td><td class="num">38</td><td class="num">0</td><td class="num col26">0</td><td class="num">38 → 0</td><td class="num dn">-38억',
         '히어로즈 테일즈</td><td class="num">85</td><td class="num">26</td><td class="num">10</td><td class="num">0</td><td class="num col26">0</td><td class="num">40 → 0</td><td class="num dn">-40억'),
        # 버섯커
        ('버섯커 키우기</td><td class="num">0</td><td class="num">0</td><td class="num">126</td><td class="num">11</td><td class="num col26">2</td><td class="num">42 → 8</td><td class="num dn">-34억',
         '아르케랜드</td><td class="num">105</td><td class="num">32</td><td class="num">0</td><td class="num">0</td><td class="num col26">0</td><td class="num">46 → 0</td><td class="num dn">-46억'),

        # KR RPG 신작 - MapleStory Idle
        ('MapleStory: Idle RPG</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">101</td><td class="num col26">487</td><td class="num">0 → 178</td><td class="num up">+178억',
         'MapleStory : Idle RPG</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">604</td><td class="num col26">487</td><td class="num">0 → 581</td><td class="num up">+581억'),
        # 마비노기
        ('마비노기 모바일</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">110</td><td class="num col26">241</td><td class="num">0 → 147</td><td class="num up">+147억',
         '마비노기 모바일</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">197</td><td class="num col26">79</td><td class="num">0 → 173</td><td class="num up">+173억'),
        # 뱀피르
        ('뱀피르</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">145</td><td class="num col26">44</td><td class="num">0 → 125</td><td class="num up">+125억',
         '뱀피르</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">348</td><td class="num col26">44</td><td class="num">0 → 287</td><td class="num up">+287억'),
        # Seven Knights
        ('Seven Knights Re:BIRTH</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">143</td><td class="num col26">36</td><td class="num">0 → 122</td><td class="num up">+122억',
         'Seven Knights Re:BIRTH</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">215</td><td class="num col26">36</td><td class="num">0 → 179</td><td class="num up">+179억'),

        # KR RPG 감소 - Lineage W
        ('Lineage W</td><td class="num">357</td><td class="num">200</td><td class="num">42</td><td class="num">71</td><td class="num col26">35</td><td class="num">200 → 59</td><td class="num dn">-141억',
         'Lineage W</td><td class="num">350</td><td class="num">144</td><td class="num">106</td><td class="num">67</td><td class="num col26">25</td><td class="num">200 → 59</td><td class="num dn">-141억'),
        # 오딘
        ('오딘: 발할라 라이징</td><td class="num">350</td><td class="num">256</td><td class="num">130</td><td class="num">155</td><td class="num col26">59</td><td class="num">245 → 123</td><td class="num dn">-122억',
         '오딘: 발할라 라이징</td><td class="num">297</td><td class="num">237</td><td class="num">201</td><td class="num">135</td><td class="num col26">73</td><td class="num">245 → 123</td><td class="num dn">-122억'),
        # 리니지2M
        ('리니지2M</td><td class="num">194</td><td class="num">133</td><td class="num">49</td><td class="num">68</td><td class="num col26">21</td><td class="num">125 → 52</td><td class="num dn">-73억',
         '리니지2M</td><td class="num">147</td><td class="num">131</td><td class="num">98</td><td class="num">59</td><td class="num col26">23</td><td class="num">125 → 52</td><td class="num dn">-73억'),
        # 리니지M
        ('리니지M</td><td class="num">406</td><td class="num">476</td><td class="num">510</td><td class="num">435</td><td class="num col26">187</td><td class="num">453 → 385</td><td class="num dn">-68억',
         '리니지M</td><td class="num">398</td><td class="num">464</td><td class="num">497</td><td class="num">435</td><td class="num col26">187</td><td class="num">453 → 385</td><td class="num dn">-68억'),
        # 나이트 크로우
        ('나이트 크로우</td><td class="num">0</td><td class="num">183</td><td class="num">50</td><td class="num">25</td><td class="num col26">7</td><td class="num">78 → 19</td><td class="num dn">-59억',
         '나이트 크로우</td><td class="num">0</td><td class="num">244</td><td class="num">50</td><td class="num">21</td><td class="num col26">12</td><td class="num">98 → 19</td><td class="num dn">-79억'),

        # Royal Match
        ('Royal Match</td><td class="num">12</td><td class="num">51</td><td class="num">129</td><td class="num">123</td><td class="num col26">96</td><td class="num">64 → 118</td><td class="num up">+54억',
         'Royal Match</td><td class="num">13</td><td class="num">51</td><td class="num">129</td><td class="num">123</td><td class="num col26">96</td><td class="num">64 → 118</td><td class="num up">+54억'),
    ]

    count = 0
    for old, new in kr_step5_replacements:
        if old in html:
            html = html.replace(old, new, 1)
            count += 1

    print(f"KR Step 5: {count}/{len(kr_step5_replacements)} replaced")

    # JP Step 5 - Key replacements
    jp_step5 = [
        # Pokémon TCG Pocket
        ('Pokémon TCG Pocket</td><td class="num">0</td><td class="num">0</td><td class="num">168</td><td class="num">343</td><td class="num col26">186</td><td class="num">42 → 312</td><td class="num up">+270億',
         'Pokémon TCG Pocket</td><td class="num">0</td><td class="num">0</td><td class="num">504</td><td class="num">343</td><td class="num col26">186</td><td class="num">168 → 312</td><td class="num up">+144億'),
        # SDガンダム
        ('SDガンダム ジージェネレーション エターナル</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">175</td><td class="num col26">340</td><td class="num">0 → 230</td><td class="num up">+230億',
         'SDガンダム ジージェネレーション エターナル</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">324</td><td class="num col26">179</td><td class="num">0 → 295</td><td class="num up">+295億'),
        # 学園アイドルマスター
        ('学園アイドルマスター</td><td class="num">0</td><td class="num">0</td><td class="num">163</td><td class="num">184</td><td class="num col26">86</td><td class="num">54 → 165</td><td class="num up">+111億',
         '学園アイドルマスター</td><td class="num">0</td><td class="num">0</td><td class="num">243</td><td class="num">184</td><td class="num col26">86</td><td class="num">81 → 164</td><td class="num up">+83億'),
        # Shadowverse
        ('Shadowverse: Worlds Beyond</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">95</td><td class="num col26">73</td><td class="num">0 → 88</td><td class="num up">+88億',
         'Shadowverse: Worlds Beyond</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">160</td><td class="num col26">67</td><td class="num">0 → 141</td><td class="num up">+141億'),
        # eFootball
        ('eFootball™</td><td class="num">170</td><td class="num">147</td><td class="num">126</td><td class="num">237</td><td class="num col26">228</td><td class="num">148 → 234</td><td class="num up">+86億',
         'eFootball™</td><td class="num">58</td><td class="num">173</td><td class="num">225</td><td class="num">235</td><td class="num col26">228</td><td class="num">152 → 234</td><td class="num up">+82億'),
        # モンスト
        ('モンスターストライク</td><td class="num">792</td><td class="num">638</td><td class="num">516</td><td class="num">405</td><td class="num col26">347</td><td class="num">649 → 389</td><td class="num dn">-260億',
         'モンスターストライク</td><td class="num">748</td><td class="num">640</td><td class="num">559</td><td class="num">398</td><td class="num col26">355</td><td class="num">649 → 389</td><td class="num dn">-260億'),
        # ウマ娘
        ('ウマ娘 プリティーダービー</td><td class="num">772</td><td class="num">503</td><td class="num">300</td><td class="num">309</td><td class="num col26">219</td><td class="num">525 → 286</td><td class="num dn">-239億',
         'ウマ娘 プリティーダービー</td><td class="num">747</td><td class="num">482</td><td class="num">345</td><td class="num">273</td><td class="num col26">337</td><td class="num">525 → 286</td><td class="num dn">-239億'),
        # FGO
        ('Fate/Grand Order</td><td class="num">562</td><td class="num">466</td><td class="num">383</td><td class="num">397</td><td class="num col26">255</td><td class="num">470 → 369</td><td class="num dn">-101億',
         'Fate/Grand Order</td><td class="num">562</td><td class="num">466</td><td class="num">383</td><td class="num">397</td><td class="num col26">255</td><td class="num">470 → 369</td><td class="num dn">-101億'),
        # ヘブバン
        ('ヘブンバーンズレッド</td><td class="num">202</td><td class="num">142</td><td class="num">63</td><td class="num">61</td><td class="num col26">12</td><td class="num">136 → 49</td><td class="num dn">-87億',
         'ヘブンバーンズレッド</td><td class="num">189</td><td class="num">131</td><td class="num">104</td><td class="num">59</td><td class="num col26">43</td><td class="num">141 → 56</td><td class="num dn">-85億'),
        # プロセカ
        ('プロジェクトセカイ カラフルステージ</td><td class="num">240</td><td class="num">173</td><td class="num">68</td><td class="num">95</td><td class="num col26">21</td><td class="num">160 → 75</td><td class="num dn">-85億',
         'プロジェクトセカイ カラフルステージ！ feat. 初音ミク</td><td class="num">193</td><td class="num">163</td><td class="num">124</td><td class="num">80</td><td class="num col26">57</td><td class="num">160 → 75</td><td class="num dn">-85億'),
        # パズドラ
        ('パズル＆ドラゴンズ</td><td class="num">357</td><td class="num">214</td><td class="num">157</td><td class="num">193</td><td class="num col26">62</td><td class="num">243 → 161</td><td class="num dn">-82億',
         'パズル＆ドラゴンズ</td><td class="num">292</td><td class="num">229</td><td class="num">207</td><td class="num">150</td><td class="num col26">205</td><td class="num">243 → 161</td><td class="num dn">-82億'),

        # 중화권 증가 - Whiteout JP
        ('Whiteout Survival</td><td class="num">0</td><td class="num">87</td><td class="num">68</td><td class="num">269</td><td class="num col26">336</td><td class="num">52 → 280</td><td class="num up">+228億',
         'Whiteout Survival</td><td class="num">0</td><td class="num">44</td><td class="num">139</td><td class="num">278</td><td class="num col26">288</td><td class="num">61 → 280</td><td class="num up">+219億'),
        # Last War JP (2 entries)
        ('Last War:Survival</td><td class="num">0</td><td class="num">0</td><td class="num">192</td><td class="num">276</td><td class="num col26">239</td><td class="num">64 → 269</td><td class="num up">+205億',
         'Last War:Survival</td><td class="num">0</td><td class="num">0</td><td class="num">191</td><td class="num">276</td><td class="num col26">239</td><td class="num">64 → 269</td><td class="num up">+205億'),
        ('Last War:Survival Game</td><td class="num">0</td><td class="num">0</td><td class="num">106</td><td class="num">196</td><td class="num col26">183</td><td class="num">35 → 194</td><td class="num up">+159億',
         'Last War:Survival Game</td><td class="num">0</td><td class="num">0</td><td class="num">105</td><td class="num">194</td><td class="num col26">194</td><td class="num">35 → 194</td><td class="num up">+159億'),
        # Wuthering Waves JP
        ('Wuthering Waves</td><td class="num">0</td><td class="num">0</td><td class="num">42</td><td class="num">97</td><td class="num col26">142</td><td class="num">14 → 110</td><td class="num up">+96億',
         'Wuthering Waves</td><td class="num">0</td><td class="num">0</td><td class="num">63</td><td class="num">105</td><td class="num col26">130</td><td class="num">21 → 110</td><td class="num up">+89億'),
        # NIKKE JP
        ('GODDESS OF VICTORY: NIKKE</td><td class="num">202</td><td class="num">191</td><td class="num">132</td><td class="num">144</td><td class="num col26">97</td><td class="num">175 → 131</td><td class="num dn">-44億',
         'GODDESS OF VICTORY: NIKKE</td><td class="num">611</td><td class="num">249</td><td class="num">173</td><td class="num">135</td><td class="num col26">117</td><td class="num">344 → 131</td><td class="num dn">-213億'),
        # Genshin JP
        ('Genshin Impact</td><td class="num">377</td><td class="num">295</td><td class="num">156</td><td class="num">175</td><td class="num col26">93</td><td class="num">276 → 151</td><td class="num dn">-125億',
         'Genshin Impact</td><td class="num">363</td><td class="num">257</td><td class="num">206</td><td class="num">144</td><td class="num col26">179</td><td class="num">275 → 151</td><td class="num dn">-124億'),
    ]

    count_jp = 0
    for old, new in jp_step5:
        if old in html:
            html = html.replace(old, new, 1)
            count_jp += 1
    print(f"JP Step 5: {count_jp}/{len(jp_step5)} replaced")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("\nDone!")

if __name__ == '__main__':
    main()
