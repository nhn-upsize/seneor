#!/usr/bin/env python3
"""Fix US panel data with new filter (in_revenue_top100_unified_os)"""
import re

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# New data (in_revenue_top100_unified_os = TRUE)
# Step 1
US = {
    'rev': {2022:14687, 2023:16355, 2024:19360, 2025:19999, 2026:18686},
    'mau': {2022:30580, 2023:29394, 2024:29386, 2025:29698, 2026:30371},
    'dl':  {2022:2953, 2023:3059, 2024:3152, 2025:3175, 2026:3197},
    'arpmau': {2022:4803, 2023:5564, 2024:6588, 2025:6734, 2026:6153},
}

# Step 2
PUB = {
    'etc': {2022:(6841,41), 2023:(7464,42), 2024:(8521,45), 2025:(8879,45), 2026:(8421,47)},
    'na':  {2022:(5067,36), 2023:(6174,35), 2024:(7326,33), 2025:(5782,30), 2026:(4607,27)},
    'zhcn':{2022:(2281,20), 2023:(2249,21), 2024:(2972,21), 2025:(4458,21), 2026:(5010,26)},
    'JP':  {2022:(301,3), 2023:(332,3), 2024:(397,2), 2025:(675,4), 2026:(487,4)},
    'KR':  {2022:(198,3), 2023:(136,2), 2024:(144,2), 2025:(205,2), 2026:(161,2)},
}

def avg_pre(d): return round((d[2022] + d[2023] + d[2024]) / 3)
def avg_post(d): return round((d[2025]*12 + d[2026]*3) / 15)

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find US panel boundaries
    us_start = html.find('<div class="ctab-panel" id="us">')
    if us_start == -1:
        print("US panel not found!")
        return

    # Replacements for US panel Step 1
    replacements = [
        # Revenue row
        ('15,180</td><td class="num up">16,816</td><td class="num up">19,832</td><td class="num up">20,461</td><td class="num col26 dn">19,213',
         f'{US["rev"][2022]:,}</td><td class="num up">{US["rev"][2023]:,}</td><td class="num up">{US["rev"][2024]:,}</td><td class="num up">{US["rev"][2025]:,}</td><td class="num col26 dn">{US["rev"][2026]:,}'),

        # Revenue pre/post
        ('17,276 → 20,211', f'{avg_pre(US["rev"]):,} \u2192 {avg_post(US["rev"]):,}'),
        ('+2,935억 (+17%)', f'+{avg_post(US["rev"])-avg_pre(US["rev"]):,}억 (+{round((avg_post(US["rev"])-avg_pre(US["rev"]))/avg_pre(US["rev"])*100)}%)'),

        # MAU row
        ('28,587</td><td class="num dn">27,783</td><td class="num up">28,394</td><td class="num dn">27,753</td><td class="num col26 dn">26,050',
         f'{US["mau"][2022]:,}</td><td class="num dn">{US["mau"][2023]:,}</td><td class="num dn">{US["mau"][2024]:,}</td><td class="num up">{US["mau"][2025]:,}</td><td class="num col26 up">{US["mau"][2026]:,}'),
        ('28,255 → 27,412', f'{avg_pre(US["mau"]):,} \u2192 {avg_post(US["mau"]):,}'),

        # ARPMAU row
        ('5,310</td><td class="num up">6,053</td><td class="num up">6,985</td><td class="num up">7,373</td><td class="num col26">7,375',
         f'{US["arpmau"][2022]:,}</td><td class="num up">{US["arpmau"][2023]:,}</td><td class="num up">{US["arpmau"][2024]:,}</td><td class="num up">{US["arpmau"][2025]:,}</td><td class="num col26 dn">{US["arpmau"][2026]:,}'),
        ('6,116 → 7,373', f'{avg_pre(US["arpmau"]):,} \u2192 {avg_post(US["arpmau"]):,}'),

        # DL values in text/SVG
        ('2,971', f'{US["dl"][2022]:,}'),
        ('3,126', f'{US["dl"][2023]:,}'),
        ('3,216万건', f'{US["dl"][2025]:,}万건'),

        # US headline
        ('월평균 매출 1.73조원 (22~24) → 2.02조원 (25~26.1Q) (+17%)',
         f'월평균 매출 {avg_pre(US["rev"])/10000:.2f}조원 (22~24) \u2192 {avg_post(US["rev"])/10000:.2f}조원 (25~26.1Q) (+{round((avg_post(US["rev"])-avg_pre(US["rev"]))/avg_pre(US["rev"])*100)}%)'),

        # Step 2 pub rows - 기타 (글로벌)
        ('7,034억', f'{PUB["etc"][2022][0]:,}억'),
        ('7,668억', f'{PUB["etc"][2023][0]:,}억'),
        ('8,696억', f'{PUB["etc"][2024][0]:,}억'),
        ('9,130억', f'{PUB["etc"][2025][0]:,}억'),
        ('8,643억', f'{PUB["etc"][2026][0]:,}억'),

        # 북미
        ('5,189억', f'{PUB["na"][2022][0]:,}억'),
        ('6,246억', f'{PUB["na"][2023][0]:,}억'),
        ('7,418억', f'{PUB["na"][2024][0]:,}억'),
        ('5,839억', f'{PUB["na"][2025][0]:,}억'),
        ('4,710억', f'{PUB["na"][2026][0]:,}억'),

        # 중화권
        ('2,381억', f'{PUB["zhcn"][2022][0]:,}억'),
        ('2,368억', f'{PUB["zhcn"][2023][0]:,}억'),
        ('3,150억', f'{PUB["zhcn"][2024][0]:,}억'),
        ('4,590억', f'{PUB["zhcn"][2025][0]:,}억'),
        ('5,129억', f'{PUB["zhcn"][2026][0]:,}억'),

        # Pre/post for US Step 2
        ('7,799억 → 9,032억', f'{avg_pre({yr: PUB["etc"][yr][0] for yr in [2022,2023,2024]}):,}억 \u2192 {avg_post({yr: PUB["etc"][yr][0] for yr in [2025,2026]}):,}억'),
        ('6,285억 → 5,613억', f'{avg_pre({yr: PUB["na"][yr][0] for yr in [2022,2023,2024]}):,}억 \u2192 {avg_post({yr: PUB["na"][yr][0] for yr in [2025,2026]}):,}억'),
        ('2,633억 → 4,698억', f'{avg_pre({yr: PUB["zhcn"][yr][0] for yr in [2022,2023,2024]}):,}억 \u2192 {avg_post({yr: PUB["zhcn"][yr][0] for yr in [2025,2026]}):,}억'),
        ('373억 → 659억', f'{avg_pre({yr: PUB["JP"][yr][0] for yr in [2022,2023,2024]}):,}억 \u2192 {avg_post({yr: PUB["JP"][yr][0] for yr in [2025,2026]}):,}억'),
        ('186억 → 209억', f'{avg_pre({yr: PUB["KR"][yr][0] for yr in [2022,2023,2024]}):,}억 \u2192 {avg_post({yr: PUB["KR"][yr][0] for yr in [2025,2026]}):,}억'),
    ]

    # Apply only within US panel section
    us_end_search = html.find('<div class="v2-footer">', us_start)
    if us_end_search == -1:
        us_end_search = len(html)

    us_section = html[us_start:us_end_search]

    count = 0
    for old, new in replacements:
        if old != new and old in us_section:
            us_section = us_section.replace(old, new, 1)
            count += 1

    html = html[:us_start] + us_section + html[us_end_search:]

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Applied {count}/{len(replacements)} US panel replacements")

if __name__ == '__main__':
    main()
