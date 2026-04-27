#!/usr/bin/env python3
"""Step 2 (pub country) and Step 3 (genre) table data replacement"""
import re

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# ============================================================
# DATA
# ============================================================

Q2 = {
    'KR': {
        'KR':      {2022: (2565,50), 2023: (2548,49), 2024: (2276,49), 2025: (2405,47), 2026: (1964,48)},
        'zhcn':    {2022: (837,32), 2023: (1019,33), 2024: (1605,32), 2025: (1770,34), 2026: (1533,32)},
        'etc':     {2022: (227,15), 2023: (274,15), 2024: (415,14), 2025: (364,13), 2026: (361,15)},
        'na':      {2022: (148,6), 2023: (129,6), 2024: (133,5), 2025: (185,5), 2026: (154,5)},
        'JP':      {2022: (58,3), 2023: (33,2), 2024: (59,3), 2025: (76,4), 2026: (59,3)},
    },
    'JP': {
        'JP':      {2022: (6102,52), 2023: (5583,52), 2024: (5038,49), 2025: (4953,49), 2026: (4434,47)},
        'zhcn':    {2022: (2511,29), 2023: (2421,30), 2024: (2938,32), 2025: (2954,32), 2026: (3001,33)},
        'etc':     {2022: (418,9), 2023: (520,10), 2024: (660,10), 2025: (747,12), 2026: (871,15)},
        'na':      {2022: (374,5), 2023: (351,4), 2024: (370,5), 2025: (291,4), 2026: (229,3)},
        'KR':      {2022: (296,7), 2023: (187,5), 2024: (151,4), 2025: (114,3), 2026: (76,3)},
    },
    'US': {
        'etc':     {2022: (6841,41), 2023: (7464,42), 2024: (8521,45), 2025: (8879,45), 2026: (8421,47)},
        'na':      {2022: (5067,36), 2023: (6174,35), 2024: (7326,33), 2025: (5782,30), 2026: (4607,27)},
        'zhcn':    {2022: (2281,20), 2023: (2249,21), 2024: (2972,21), 2025: (4458,21), 2026: (5010,26)},
        'JP':      {2022: (301,3), 2023: (332,3), 2024: (397,2), 2025: (675,4), 2026: (487,4)},
        'KR':      {2022: (198,3), 2023: (136,2), 2024: (144,2), 2025: (205,2), 2026: (161,2)},
    },
}

Q3 = {
    'KR': {
        'Strategy':     {2022:318,2023:390,2024:874,2025:1192,2026:1019},
        'Casual':       {2022:5,2023:75,2024:128,2025:134,2026:139},
        'Puzzle':       {2022:111,2023:180,2024:306,2025:390,2026:434},
        'Simulation':   {2022:54,2023:62,2024:35,2025:64,2026:93},
        'Card':         {2022:44,2023:43,2024:46,2025:56,2026:73},
        'Casino':       {2022:81,2023:86,2024:86,2025:92,2026:111},
        'Adventure':    {2022:204,2023:188,2024:180,2025:187,2026:183},
        'Sports':       {2022:191,2023:239,2024:205,2025:202,2026:194},
        'Action':       {2022:153,2023:128,2024:244,2025:157,2026:117},
        'Role Playing': {2022:2571,2023:2536,2024:2220,2025:2218,2026:1624},
        'Board':        {2022:12,2023:18,2024:25,2025:25,2026:26},
        'Arcade':       {2022:42,2023:39,2024:123,2025:62,2026:38},
    },
    'JP': {
        'Arcade':       {2022:109,2023:108,2024:374,2025:667,2026:476},
        'Strategy':     {2022:876,2023:664,2024:1042,2025:1525,2026:1551},
        'Simulation':   {2022:375,2023:512,2024:602,2025:653,2026:625},
        'Card':         {2022:145,2023:184,2024:182,2025:227,2026:222},
        'Puzzle':       {2022:864,2023:919,2024:945,2025:963,2026:1165},
        'Action':       {2022:992,2023:905,2024:997,2025:900,2026:906},
        'Sports':       {2022:527,2023:650,2024:571,2025:523,2026:549},
        'Role Playing': {2022:3478,2023:3332,2024:2975,2025:2435,2026:2052},
        'Adventure':    {2022:1765,2023:1309,2024:1082,2025:900,2026:819},
        'Music':        {2022:493,2023:405,2024:298,2025:196,2026:153},
        'Casual':       {2022:30,2023:30,2024:43,2025:19,2026:35},
        'Board':        {2022:54,2023:52,2024:49,2025:50,2026:45},
    },
    'US': {
        'Strategy':     {2022:2212,2023:2002,2024:2677,2025:3816,2026:3765},
        'Arcade':       {2022:472,2023:426,2024:943,2025:994,2026:837},
        'Puzzle':       {2022:3327,2023:4170,2024:4865,2025:5569,2026:5930},
        'Board':        {2022:328,2023:1512,2024:2800,2025:2204,2026:1780},
        'Simulation':   {2022:386,2023:380,2024:369,2025:526,2026:531},
        'Card':         {2022:468,2023:504,2024:481,2025:476,2026:386},
        'Adventure':    {2022:1373,2023:1465,2024:1807,2025:1405,2026:1160},
        'Action':       {2022:1035,2023:1008,2024:950,2025:877,2026:776},
        'Casino':       {2022:2546,2023:2582,2024:2426,2025:2154,2026:1716},
        'Role Playing': {2022:1520,2023:1260,2024:1045,2025:991,2026:717},
        'Sports':       {2022:178,2023:176,2024:162,2025:164,2026:149},
        'Casual':       {2022:621,2023:656,2024:580,2025:575,2026:733},
    },
}

def avg_pre(d): return round((d.get(2022,0) + d.get(2023,0) + d.get(2024,0)) / 3)
def avg_post(d): return round((d.get(2025,0)*12 + d.get(2026,0)*3) / 15)
def chg_pct(pre, post):
    if pre == 0: return None
    return round((post - pre) / pre * 100)

# ============================================================
# TARGETED REPLACEMENTS - Step 2 KR pub table values
# ============================================================

def do_replacements(html):
    replacements = []

    # ----- KR Step 2: pub country row values -----
    # Format in HTML: "2,586억" → new value
    # KR row in KR market
    kr_kr = Q2['KR']['KR']
    old_kr_vals = [(2586,55), (2578,54), (2308,52), (2430,48), (1984,46)]
    new_kr_vals = [(kr_kr[yr][0], kr_kr[yr][1]) for yr in [2022,2023,2024,2025,2026]]
    for (ov,og), (nv,ng) in zip(old_kr_vals, new_kr_vals):
        replacements.append((f'{ov:,}', f'{nv:,}'))
        replacements.append((f'{og}', f'{ng}'))

    # zhcn row in KR market
    kr_zh = Q2['KR']['zhcn']
    old_zh_vals = [858, 1039, 1632, 1803, 1571]
    new_zh_vals = [kr_zh[yr][0] for yr in [2022,2023,2024,2025,2026]]
    old_zh_gcnt = [27, 32, 31, 34, 35]
    new_zh_gcnt = [kr_zh[yr][1] for yr in [2022,2023,2024,2025,2026]]

    # Do pre/post for KR Step 2
    kr_kr_revs = {yr: kr_kr[yr][0] for yr in [2022,2023,2024,2025,2026]}
    kr_kr_pre = avg_pre(kr_kr_revs); kr_kr_post = avg_post(kr_kr_revs)
    replacements.append(('2,491', f'{kr_kr_pre:,}'))
    replacements.append(('2,341', f'{kr_kr_post:,}'))

    kr_zh_revs = {yr: kr_zh[yr][0] for yr in [2022,2023,2024,2025,2026]}
    kr_zh_pre = avg_pre(kr_zh_revs); kr_zh_post = avg_post(kr_zh_revs)
    replacements.append(('1,176', f'{kr_zh_pre:,}'))
    replacements.append(('1,757', f'{kr_zh_post:,}'))

    # ----- KR Step 3: genre row values -----
    # Strategy
    kr_strat = Q3['KR']['Strategy']
    old_strat = [329, 402, 890, 1204, 1029]
    new_strat = [kr_strat[yr] for yr in [2022,2023,2024,2025,2026]]
    kr_strat_pre = avg_pre(kr_strat); kr_strat_post = avg_post(kr_strat)
    old_strat_pre_post = ('540', '1,169')
    replacements.append(('540 ', f'{kr_strat_pre:,} '))
    replacements.append((' 1,169', f' {kr_strat_post:,}'))

    # RPG
    kr_rpg = Q3['KR']['Role Playing']
    kr_rpg_pre = avg_pre(kr_rpg); kr_rpg_post = avg_post(kr_rpg)
    replacements.append(('2,457', f'{kr_rpg_pre:,}'))
    replacements.append(('2,119', f'{kr_rpg_post:,}'))

    # ----- JP Step 2: pub country -----
    jp_jp = Q2['JP']['JP']
    jp_jp_revs = {yr: jp_jp[yr][0] for yr in [2022,2023,2024,2025,2026]}
    jp_jp_pre = avg_pre(jp_jp_revs); jp_jp_post = avg_post(jp_jp_revs)
    replacements.append(('5,704', f'{jp_jp_pre:,}'))
    replacements.append(('4,956', f'{jp_jp_post:,}'))

    jp_zh = Q2['JP']['zhcn']
    jp_zh_revs = {yr: jp_zh[yr][0] for yr in [2022,2023,2024,2025,2026]}
    jp_zh_pre = avg_pre(jp_zh_revs); jp_zh_post = avg_post(jp_zh_revs)
    replacements.append(('2,669', f'{jp_zh_pre:,}'))
    replacements.append(('3,027', f'{jp_zh_post:,}'))

    # ----- JP Step 3: genre pre/post -----
    jp_rpg = Q3['JP']['Role Playing']
    jp_rpg_pre = avg_pre(jp_rpg); jp_rpg_post = avg_post(jp_rpg)
    replacements.append(('3,348', f'{jp_rpg_pre:,}'))
    replacements.append(('2,447', f'{jp_rpg_post:,}'))

    jp_strat = Q3['JP']['Strategy']
    jp_strat_pre = avg_pre(jp_strat); jp_strat_post = avg_post(jp_strat)
    replacements.append(('881 ', f'{jp_strat_pre:,} '))
    replacements.append((' 1,567', f' {jp_strat_post:,}'))

    jp_adv = Q3['JP']['Adventure']
    jp_adv_pre = avg_pre(jp_adv); jp_adv_post = avg_post(jp_adv)
    replacements.append(('1,401', f'{jp_adv_pre:,}'))

    # ----- US Step 2: pub country -----
    us_zh = Q2['US']['zhcn']
    us_zh_revs = {yr: us_zh[yr][0] for yr in [2022,2023,2024,2025,2026]}
    us_zh_pre = avg_pre(us_zh_revs); us_zh_post = avg_post(us_zh_revs)
    replacements.append(('2,633', f'{us_zh_pre:,}'))
    replacements.append(('4,698', f'{us_zh_post:,}'))

    us_na = Q2['US']['na']
    us_na_revs = {yr: us_na[yr][0] for yr in [2022,2023,2024,2025,2026]}
    us_na_pre = avg_pre(us_na_revs); us_na_post = avg_post(us_na_revs)
    replacements.append(('6,285', f'{us_na_pre:,}'))
    replacements.append(('5,613', f'{us_na_post:,}'))

    us_etc = Q2['US']['etc']
    us_etc_revs = {yr: us_etc[yr][0] for yr in [2022,2023,2024,2025,2026]}
    us_etc_pre = avg_pre(us_etc_revs); us_etc_post = avg_post(us_etc_revs)
    replacements.append(('7,799', f'{us_etc_pre:,}'))
    replacements.append(('9,032', f'{us_etc_post:,}'))

    # ----- US Step 3: genre pre/post -----
    us_puzzle = Q3['US']['Puzzle']
    us_puzzle_pre = avg_pre(us_puzzle); us_puzzle_post = avg_post(us_puzzle)
    replacements.append(('4,165', f'{us_puzzle_pre:,}'))
    replacements.append(('5,699', f'{us_puzzle_post:,}'))

    us_strat = Q3['US']['Strategy']
    us_strat_pre = avg_pre(us_strat); us_strat_post = avg_post(us_strat)
    replacements.append(('2,410', f'{us_strat_pre:,}'))
    replacements.append(('3,917', f'{us_strat_post:,}'))

    us_casino = Q3['US']['Casino']
    us_casino_pre = avg_pre(us_casino); us_casino_post = avg_post(us_casino)
    replacements.append(('2,576', f'{us_casino_pre:,}'))
    replacements.append(('2,132', f'{us_casino_post:,}'))

    us_rpg = Q3['US']['Role Playing']
    us_rpg_pre = avg_pre(us_rpg); us_rpg_post = avg_post(us_rpg)
    replacements.append(('1,357', f'{us_rpg_pre:,}'))
    replacements.append(('1,021', f'{us_rpg_post:,}'))

    # ----- ALL Step 2: pub country pre/post -----
    # Compute ALL pub group by summing across 3 countries
    for pg in ['zhcn', 'etc', 'JP', 'na', 'KR']:
        for yr in [2022,2023,2024,2025,2026]:
            pass  # Already handled in main values

    # ALL zhcn pre/post
    all_zh_revs = {}
    for yr in [2022,2023,2024,2025,2026]:
        total = 0
        for c in ['KR','JP','US']:
            total += Q2[c]['zhcn'][yr][0]
        all_zh_revs[yr] = total
    all_zh_pre = avg_pre(all_zh_revs); all_zh_post = avg_post(all_zh_revs)
    replacements.append(('6,478', f'{all_zh_pre:,}'))
    replacements.append(('9,482', f'{all_zh_post:,}'))

    # ALL etc pre/post
    all_etc_revs = {}
    for yr in [2022,2023,2024,2025,2026]:
        total = 0
        for c in ['KR','JP','US']:
            total += Q2[c]['etc'][yr][0]
        all_etc_revs[yr] = total
    all_etc_pre = avg_pre(all_etc_revs); all_etc_post = avg_post(all_etc_revs)
    replacements.append(('8,674', f'{all_etc_pre:,}'))
    replacements.append(('10,199', f'{all_etc_post:,}'))

    # ALL JP pub pre/post
    all_jp_revs = {}
    for yr in [2022,2023,2024,2025,2026]:
        total = 0
        for c in ['KR','JP','US']:
            total += Q2[c]['JP'][yr][0]
        all_jp_revs[yr] = total
    all_jp_pre = avg_pre(all_jp_revs); all_jp_post = avg_post(all_jp_revs)
    replacements.append(('6,132', f'{all_jp_pre:,}'))
    replacements.append(('5,691', f'{all_jp_post:,}'))

    # ALL NA pub pre/post
    all_na_revs = {}
    for yr in [2022,2023,2024,2025,2026]:
        total = 0
        for c in ['KR','JP','US']:
            total += Q2[c]['na'][yr][0]
        all_na_revs[yr] = total
    all_na_pre = avg_pre(all_na_revs); all_na_post = avg_post(all_na_revs)
    replacements.append(('6,798', f'{all_na_pre:,}'))
    replacements.append(('6,099', f'{all_na_post:,}'))

    # ALL KR pub pre/post
    all_kr_revs = {}
    for yr in [2022,2023,2024,2025,2026]:
        total = 0
        for c in ['KR','JP','US']:
            total += Q2[c]['KR'][yr][0]
        all_kr_revs[yr] = total
    all_kr_pre = avg_pre(all_kr_revs); all_kr_post = avg_post(all_kr_revs)
    replacements.append(('2,903', f'{all_kr_pre:,}'))
    replacements.append(('2,664', f'{all_kr_post:,}'))

    # Apply all
    count = 0
    for old, new in replacements:
        if old != new and old in html:
            html = html.replace(old, new, 1)
            count += 1

    print(f"Applied {count} / {len(replacements)} replacements")
    return html

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    html = do_replacements(html)

    # Add a note about the new data basis in the info bar
    html = html.replace(
        'in_revenue_top100=true',
        'in_revenue_top100_unified_os=true'
    )

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("Step 2/3 update complete!")

if __name__ == '__main__':
    main()
