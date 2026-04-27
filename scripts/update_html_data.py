#!/usr/bin/env python3
"""
HTML 리포트 수치 전면 교체 스크립트
기준 변경: in_revenue_top100 → in_revenue_top100_unified_os (iOS+Android 합산 TOP100)
"""
import re, json, copy

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
OUT_PATH  = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# ============================================================
# 1. RAW QUERY DATA (from DB queries with new filter)
# ============================================================

# Q1: 국가별 연도별 월평균 (rev=억원, mau=만명, dl=만건, arpmau=원)
Q1 = {
    'KR': {
        2022: {'rev': 3835, 'mau': 4291, 'dl': 569, 'arpmau': 8938},
        2023: {'rev': 4003, 'mau': 4090, 'dl': 557, 'arpmau': 9787},
        2024: {'rev': 4488, 'mau': 3661, 'dl': 620, 'arpmau': 12258},
        2025: {'rev': 4800, 'mau': 3619, 'dl': 549, 'arpmau': 13263},
        2026: {'rev': 4071, 'mau': 3599, 'dl': 497, 'arpmau': 11312},
    },
    'JP': {
        2022: {'rev': 9700, 'mau': 10158, 'dl': 757, 'arpmau': 9549},
        2023: {'rev': 9062, 'mau': 9588, 'dl': 851, 'arpmau': 9451},
        2024: {'rev': 9157, 'mau': 8647, 'dl': 802, 'arpmau': 10591},
        2025: {'rev': 9058, 'mau': 8716, 'dl': 716, 'arpmau': 10392},
        2026: {'rev': 8611, 'mau': 8466, 'dl': 726, 'arpmau': 10171},
    },
    'US': {
        2022: {'rev': 14687, 'mau': 30580, 'dl': 2953, 'arpmau': 4803},
        2023: {'rev': 16355, 'mau': 29394, 'dl': 3059, 'arpmau': 5564},
        2024: {'rev': 19360, 'mau': 29386, 'dl': 3152, 'arpmau': 6588},
        2025: {'rev': 19999, 'mau': 29698, 'dl': 3175, 'arpmau': 6734},
        2026: {'rev': 18686, 'mau': 30371, 'dl': 3197, 'arpmau': 6153},
    }
}

# Compute ALL = sum of 3 countries
Q1['ALL'] = {}
for yr in [2022, 2023, 2024, 2025, 2026]:
    rev_sum = sum(Q1[c][yr]['rev'] for c in ['KR','JP','US'])
    mau_sum = sum(Q1[c][yr]['mau'] for c in ['KR','JP','US'])
    dl_sum  = sum(Q1[c][yr]['dl']  for c in ['KR','JP','US'])
    arpmau  = round(rev_sum * 1e8 / (mau_sum * 1e4)) if mau_sum else 0
    Q1['ALL'][yr] = {'rev': rev_sum, 'mau': mau_sum, 'dl': dl_sum, 'arpmau': arpmau}

# Q2: 퍼블리셔 국적별 (rev=억원, gcnt=게임수)
Q2 = {
    'KR': {
        '중화권':  {2022: (837,32), 2023: (1019,33), 2024: (1605,32), 2025: (1770,34), 2026: (1533,32)},
        'KR':      {2022: (2565,50), 2023: (2548,49), 2024: (2276,49), 2025: (2405,47), 2026: (1964,48)},
        '기타':    {2022: (227,15), 2023: (274,15), 2024: (415,14), 2025: (364,13), 2026: (361,15)},
        '북미':    {2022: (148,6), 2023: (129,6), 2024: (133,5), 2025: (185,5), 2026: (154,5)},
        'JP':      {2022: (58,3), 2023: (33,2), 2024: (59,3), 2025: (76,4), 2026: (59,3)},
    },
    'JP': {
        'JP':      {2022: (6102,52), 2023: (5583,52), 2024: (5038,49), 2025: (4953,49), 2026: (4434,47)},
        '중화권':  {2022: (2511,29), 2023: (2421,30), 2024: (2938,32), 2025: (2954,32), 2026: (3001,33)},
        '기타':    {2022: (418,9), 2023: (520,10), 2024: (660,10), 2025: (747,12), 2026: (871,15)},
        '북미':    {2022: (374,5), 2023: (351,4), 2024: (370,5), 2025: (291,4), 2026: (229,3)},
        'KR':      {2022: (296,7), 2023: (187,5), 2024: (151,4), 2025: (114,3), 2026: (76,3)},
    },
    'US': {
        '기타':    {2022: (6841,41), 2023: (7464,42), 2024: (8521,45), 2025: (8879,45), 2026: (8421,47)},
        '북미':    {2022: (5067,36), 2023: (6174,35), 2024: (7326,33), 2025: (5782,30), 2026: (4607,27)},
        '중화권':  {2022: (2281,20), 2023: (2249,21), 2024: (2972,21), 2025: (4458,21), 2026: (5010,26)},
        'JP':      {2022: (301,3), 2023: (332,3), 2024: (397,2), 2025: (675,4), 2026: (487,4)},
        'KR':      {2022: (198,3), 2023: (136,2), 2024: (144,2), 2025: (205,2), 2026: (161,2)},
    },
}

# Q3: 장르별 (rev=억원)
Q3 = {
    'KR': {
        'Role Playing': {2022:2571,2023:2536,2024:2220,2025:2218,2026:1624},
        'Strategy':     {2022:318,2023:390,2024:874,2025:1192,2026:1019},
        'Puzzle':       {2022:111,2023:180,2024:306,2025:390,2026:434},
        'Casino':       {2022:81,2023:86,2024:86,2025:92,2026:111},
        'Sports':       {2022:191,2023:239,2024:205,2025:202,2026:194},
        'Adventure':    {2022:204,2023:188,2024:180,2025:187,2026:183},
        'Action':       {2022:153,2023:128,2024:244,2025:157,2026:117},
        'Casual':       {2022:5,2023:75,2024:128,2025:134,2026:139},
        'Card':         {2022:44,2023:43,2024:46,2025:56,2026:73},
        'Simulation':   {2022:54,2023:62,2024:35,2025:64,2026:93},
        'Board':        {2022:12,2023:18,2024:25,2025:25,2026:26},
        'Arcade':       {2022:42,2023:39,2024:123,2025:62,2026:38},
    },
    'JP': {
        'Role Playing': {2022:3478,2023:3332,2024:2975,2025:2435,2026:2052},
        'Strategy':     {2022:876,2023:664,2024:1042,2025:1525,2026:1551},
        'Puzzle':       {2022:864,2023:919,2024:945,2025:963,2026:1165},
        'Action':       {2022:992,2023:905,2024:997,2025:900,2026:906},
        'Adventure':    {2022:1765,2023:1309,2024:1082,2025:900,2026:819},
        'Sports':       {2022:527,2023:650,2024:571,2025:523,2026:549},
        'Music':        {2022:493,2023:405,2024:298,2025:196,2026:153},
        'Simulation':   {2022:375,2023:512,2024:602,2025:653,2026:625},
        'Card':         {2022:145,2023:184,2024:182,2025:227,2026:222},
        'Arcade':       {2022:109,2023:108,2024:374,2025:667,2026:476},
        'Board':        {2022:54,2023:52,2024:49,2025:50,2026:45},
        'Casual':       {2022:30,2023:30,2024:43,2025:19,2026:35},
    },
    'US': {
        'Puzzle':       {2022:3327,2023:4170,2024:4865,2025:5569,2026:5930},
        'Casino':       {2022:2546,2023:2582,2024:2426,2025:2154,2026:1716},
        'Strategy':     {2022:2212,2023:2002,2024:2677,2025:3816,2026:3765},
        'Role Playing': {2022:1520,2023:1260,2024:1045,2025:991,2026:717},
        'Adventure':    {2022:1373,2023:1465,2024:1807,2025:1405,2026:1160},
        'Action':       {2022:1035,2023:1008,2024:950,2025:877,2026:776},
        'Board':        {2022:328,2023:1512,2024:2800,2025:2204,2026:1780},
        'Casual':       {2022:621,2023:656,2024:580,2025:575,2026:733},
        'Card':         {2022:468,2023:504,2024:481,2025:476,2026:386},
        'Arcade':       {2022:472,2023:426,2024:943,2025:994,2026:837},
        'Simulation':   {2022:386,2023:380,2024:369,2025:526,2026:531},
        'Sports':       {2022:178,2023:176,2024:162,2025:164,2026:149},
    },
}

# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def avg_pre(d):
    """22~24 평균 (전)"""
    return round((d.get(2022,0) + d.get(2023,0) + d.get(2024,0)) / 3)

def avg_post(d):
    """25~26.1Q 가중 평균 (후) = (25년×12 + 26.1Q×3) / 15"""
    return round((d.get(2025,0)*12 + d.get(2026,0)*3) / 15)

def chg_pct(pre, post):
    if pre == 0: return None
    return round((post - pre) / pre * 100)

def fmt_num(n, comma=True):
    """숫자 포맷: 콤마 추가"""
    if n is None: return '-'
    if comma:
        return f"{n:,}"
    return str(n)

def fmt_조(n):
    """억원을 조로 변환 (1만억 이상)"""
    if n >= 10000:
        return f"{n/10000:.2f}조"
    return f"{n:,}억"

def up_dn_class(val):
    if val > 0: return 'up'
    if val < 0: return 'dn'
    return ''

def up_dn_span(val, fmt=''):
    cls = up_dn_class(val)
    sign = '+' if val > 0 else ''
    if fmt == 'pct':
        return f'<span class="{cls}">{sign}{val}%</span>'
    return f'<span class="{cls}">{sign}{val:,}</span>'

# ============================================================
# 3. COMPUTE ALL DERIVED VALUES
# ============================================================

def compute_summary(country_data):
    """Compute summary stats for a country"""
    revs = {yr: country_data[yr]['rev'] for yr in [2022,2023,2024,2025,2026]}
    pre = avg_pre(revs)
    post = avg_post(revs)
    delta = post - pre
    pct = chg_pct(pre, post)
    return {
        'revs': revs, 'pre': pre, 'post': post,
        'delta': delta, 'pct': pct,
        'yoy': {
            2023: chg_pct(revs[2022], revs[2023]),
            2024: chg_pct(revs[2023], revs[2024]),
            2025: chg_pct(revs[2024], revs[2025]),
            2026: chg_pct(revs[2025], revs[2026]),
        }
    }

summaries = {c: compute_summary(Q1[c]) for c in ['KR','JP','US','ALL']}

# ============================================================
# 4. REPLACEMENT LOGIC
# ============================================================

def read_html():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def write_html(content):
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

def replace_between(html, start_marker, end_marker, new_content):
    """Replace content between two markers (markers inclusive)"""
    pattern = re.escape(start_marker) + r'.*?' + re.escape(end_marker)
    return re.sub(pattern, start_marker + new_content + end_marker, html, count=1, flags=re.DOTALL)

# --- Summary card generation ---
def gen_summary_card(country, flag, name, color, summary):
    s = summary
    trend_cls = 'up' if s['pct'] > 0 else ('down' if s['pct'] < 0 else 'flat')
    trend_label = f"{'성장' if s['pct']>0 else '하락'} {'+' if s['pct']>0 else ''}{s['pct']}%"

    # SVG sparkline points
    vals = [s['revs'][yr] for yr in [2022,2023,2024,2025,2026]]
    mn, mx = min(vals), max(vals)
    rng = mx - mn if mx != mn else 1
    xs = [20, 85, 150, 215, 280]
    ys = [round(50 - (v - mn) / rng * 40 + 10, 1) for v in vals]

    poly_pts = ' '.join(f"{x},{y}" for x,y in zip(xs,ys)) + f' 280,60 20,60'
    line_pts = ' '.join(f"{x},{y}" for x,y in zip(xs,ys))

    yoy_colors = []
    for yr in [2023,2024,2025,2026]:
        p = s['yoy'][yr]
        if p and p > 0:
            yoy_colors.append(('color:#059669;', f'+{p}%'))
        elif p and p < 0:
            yoy_colors.append(('color:#dc2626;', f'{p}%'))
        else:
            yoy_colors.append(('', '0%'))

    sign = '+' if s['delta'] > 0 else ''

    return f'''
    <div class="country-card {country.lower()}" onclick="swCountry('{country.lower()}')">
      <div class="cc-head">
        <div><span class="cc-flag">{flag}</span> <span class="cc-title">{name}</span></div>
        <span class="cc-trend {trend_cls}">{trend_label}</span>
      </div>
      <table class="cc-table">
        <thead><tr><th>연도</th><th>월평균</th><th>변화</th></tr></thead>
        <tbody>
          <tr><td>2022</td><td>{fmt_조(s['revs'][2022])}</td><td>-</td></tr>
          <tr><td>2023</td><td>{fmt_조(s['revs'][2023])}</td><td style="{yoy_colors[0][0]}">{yoy_colors[0][1]}</td></tr>
          <tr><td>2024</td><td>{fmt_조(s['revs'][2024])}</td><td style="{yoy_colors[1][0]}">{yoy_colors[1][1]}</td></tr>
          <tr><td>2025</td><td>{fmt_조(s['revs'][2025])}</td><td style="{yoy_colors[2][0]}">{yoy_colors[2][1]}</td></tr>
          <tr class="col-26"><td>26.1Q</td><td>{fmt_조(s['revs'][2026])}</td><td style="{yoy_colors[3][0]}">{yoy_colors[3][1]}</td></tr>
        </tbody>
      </table>
      <svg viewBox="0 0 300 60" style="width:100%;height:52px;margin-top:10px;" preserveAspectRatio="none">
        <defs><linearGradient id="{country.lower()}-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{color}" stop-opacity="0.3"/><stop offset="100%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
        <polygon fill="url(#{country.lower()}-grad)" points="{poly_pts}"/>
        <polyline fill="none" stroke="{color}" stroke-width="2" points="{line_pts}"/>
        <circle cx="{xs[0]}" cy="{ys[0]}" r="2.5" fill="{color}"/>
        <circle cx="{xs[1]}" cy="{ys[1]}" r="2.5" fill="{color}"/>
        <circle cx="{xs[2]}" cy="{ys[2]}" r="2.5" fill="{color}"/>
        <circle cx="{xs[3]}" cy="{ys[3]}" r="2.5" fill="{color}"/>
        <circle cx="{xs[4]}" cy="{ys[4]}" r="3.5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
      </svg>
      <div class="cc-go">25년 전후 (월평균): {fmt_조(s['pre'])} → {fmt_조(s['post'])} ({sign}{s['delta']:,}억, {sign}{s['pct']}%) ▸</div>
    </div>'''


def gen_step1_table(c, data):
    """Generate Step 1 MAU×ARPMAU table for a country"""
    revs = {yr: data[yr]['rev'] for yr in [2022,2023,2024,2025,2026]}
    maus = {yr: data[yr]['mau'] for yr in [2022,2023,2024,2025,2026]}
    arps = {yr: data[yr]['arpmau'] for yr in [2022,2023,2024,2025,2026]}
    dls  = {yr: data[yr]['dl'] for yr in [2022,2023,2024,2025,2026]}

    rev_pre = avg_pre(revs); rev_post = avg_post(revs)
    mau_pre = avg_pre(maus); mau_post = avg_post(maus)
    arp_pre = avg_pre(arps); arp_post = avg_post(arps)
    dl_pre = avg_pre(dls); dl_post = avg_post(dls)

    rev_delta = rev_post - rev_pre; rev_pct = chg_pct(rev_pre, rev_post)
    mau_delta = mau_post - mau_pre; mau_pct = chg_pct(mau_pre, mau_post)
    arp_delta = arp_post - arp_pre; arp_pct = chg_pct(arp_pre, arp_post)
    dl_delta = dl_post - dl_pre; dl_pct = chg_pct(dl_pre, dl_post)

    def td_cls(yr, metric, prev_yr=None):
        if prev_yr is None: return ''
        if metric[yr] > metric[prev_yr]: return ' up'
        if metric[yr] < metric[prev_yr]: return ' dn'
        return ''

    return {
        'rev': revs, 'mau': maus, 'arp': arps, 'dl': dls,
        'rev_pre': rev_pre, 'rev_post': rev_post, 'rev_delta': rev_delta, 'rev_pct': rev_pct,
        'mau_pre': mau_pre, 'mau_post': mau_post, 'mau_delta': mau_delta, 'mau_pct': mau_pct,
        'arp_pre': arp_pre, 'arp_post': arp_post, 'arp_delta': arp_delta, 'arp_pct': arp_pct,
        'dl_pre': dl_pre, 'dl_post': dl_post, 'dl_delta': dl_delta, 'dl_pct': dl_pct,
    }


# ============================================================
# 5. MAIN - Apply replacements
# ============================================================

def main():
    html = read_html()

    # --- A) Replace summary cards ---
    cards_html = f'''
  <div class="summary-grid">

    {gen_summary_card('KR', '🇰🇷', 'KR 한국', '#3b82f6', summaries['KR'])}

    {gen_summary_card('JP', '🇯🇵', 'JP 일본', '#ef4444', summaries['JP'])}

    {gen_summary_card('US', '🇺🇸', 'US 미국', '#a855f7', summaries['US'])}

  </div>'''

    # Replace summary grid
    html = re.sub(
        r'<div class="summary-grid">.*?</div>\s*</div>\s*</div>',
        cards_html + '\n</div>',
        html, count=1, flags=re.DOTALL
    )

    # --- B) Replace ALL panel headline ---
    all_s = summaries['ALL']
    sign = '+' if all_s['delta'] > 0 else ''
    all_headline = f'🌏 전체 시장 (KR+JP+US 합산): 월평균 매출 {fmt_num(all_s["pre"])}억 → {fmt_num(all_s["post"])}억 ({sign}{all_s["pct"]}%)'
    html = re.sub(
        r'🌏 전체 시장 \(KR\+JP\+US 합산\): 월평균 매출.*?</h2>',
        f'{all_headline}</h2>',
        html, count=1
    )

    # --- C) Replace country headlines ---
    for c, flag, name, s in [
        ('KR', '🇰🇷', '한국 시장', summaries['KR']),
        ('JP', '🇯🇵', '일본 시장', summaries['JP']),
        ('US', '🇺🇸', '미국 시장', summaries['US']),
    ]:
        sign = '+' if s['delta'] > 0 else ''
        rev_pre_fmt = fmt_조(s['pre'])
        rev_post_fmt = fmt_조(s['post'])
        new_h2 = f'{flag} {name}: 월평균 매출 {rev_pre_fmt} (22~24) → {rev_post_fmt} (25~26.1Q) ({sign}{s["pct"]}%)'
        # Match existing headline pattern
        pattern = f'{flag} {name}: 월평균 매출.*?</h2>'
        html = re.sub(pattern, f'{new_h2}</h2>', html, count=1)

    # --- D) Replace Step 1 table data for each country ---
    for c in ['ALL', 'KR', 'JP', 'US']:
        data = Q1[c]
        s1 = gen_step1_table(c, data)

        # Replace revenue row values
        for yr in [2022, 2023, 2024, 2025, 2026]:
            # These patterns are too fragile for regex, but we do targeted replacements
            pass

    # --- E) Use targeted number replacements ---
    # Since the HTML structure is complex, we use a more surgical approach:
    # Replace specific known values from old data with new data.

    # Map of old→new values for each section (context-aware)
    # ALL panel Step 1 revenue row
    replacements = [
        # ===== ALL panel =====
        # ALL headline sub-text (매출 MAU ARPMAU changes)
        # Revenue: old was 30,985→34,133 (+10%)
        ('30,985 → 34,133', f'{fmt_num(all_s["pre"])} → {fmt_num(all_s["post"])}'),
        ('+3,148억 (+10%)', f'{sign}{all_s["delta"]:,}억 ({sign}{all_s["pct"]}%)'),

        # ALL Step 1 table - revenue row
        ('28,983</td><td class="num up">30,194</td><td class="num up">33,777</td><td class="num up">34,619</td><td class="num col26 dn">32,187',
         f'{Q1["ALL"][2022]["rev"]:,}</td><td class="num{"" if Q1["ALL"][2023]["rev"]<=Q1["ALL"][2022]["rev"] else " up"}">{Q1["ALL"][2023]["rev"]:,}</td><td class="num{"" if Q1["ALL"][2024]["rev"]<=Q1["ALL"][2023]["rev"] else " up"}">{Q1["ALL"][2024]["rev"]:,}</td><td class="num{"" if Q1["ALL"][2025]["rev"]<=Q1["ALL"][2024]["rev"] else " up"}">{Q1["ALL"][2025]["rev"]:,}</td><td class="num col26{"" if Q1["ALL"][2026]["rev"]>=Q1["ALL"][2025]["rev"] else " dn"}">{Q1["ALL"][2026]["rev"]:,}'),

        # ALL Step 1 - MAU row
        ('43,097</td><td class="num dn">41,517</td><td class="num dn">40,645</td><td class="num dn">39,967</td><td class="num col26 dn">38,187',
         f'{Q1["ALL"][2022]["mau"]:,}</td><td class="num dn">{Q1["ALL"][2023]["mau"]:,}</td><td class="num dn">{Q1["ALL"][2024]["mau"]:,}</td><td class="num dn">{Q1["ALL"][2025]["mau"]:,}</td><td class="num col26 dn">{Q1["ALL"][2026]["mau"]:,}'),

        # ALL Step 1 - ARPMAU row
        ('6,725</td><td class="num up">7,273</td><td class="num up">8,310</td><td class="num up">8,662</td><td class="num col26 dn">8,429',
         f'{Q1["ALL"][2022]["arpmau"]:,}</td><td class="num up">{Q1["ALL"][2023]["arpmau"]:,}</td><td class="num up">{Q1["ALL"][2024]["arpmau"]:,}</td><td class="num up">{Q1["ALL"][2025]["arpmau"]:,}</td><td class="num col26 dn">{Q1["ALL"][2026]["arpmau"]:,}'),

        # ALL pre/post values
        ('30,985 → 34,133', f'{all_s["pre"]:,} → {all_s["post"]:,}'),
        ('41,753 → 39,611', f'{avg_pre({yr: Q1["ALL"][yr]["mau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["ALL"][yr]["mau"] for yr in [2025,2026]}):,}'),
        ('7,436 → 8,615', f'{avg_pre({yr: Q1["ALL"][yr]["arpmau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["ALL"][yr]["arpmau"] for yr in [2025,2026]}):,}'),

        # ===== KR panel =====
        # KR Step 1 revenue row
        ('3,894</td><td class="num up">4,080</td><td class="num up">4,570</td><td class="num up">4,886</td><td class="num col26 dn">4,159',
         f'{Q1["KR"][2022]["rev"]:,}</td><td class="num up">{Q1["KR"][2023]["rev"]:,}</td><td class="num up">{Q1["KR"][2024]["rev"]:,}</td><td class="num up">{Q1["KR"][2025]["rev"]:,}</td><td class="num col26 dn">{Q1["KR"][2026]["rev"]:,}'),
        ('4,181 → 4,741', f'{summaries["KR"]["pre"]:,} → {summaries["KR"]["post"]:,}'),
        ('+559억 (+13%)', f'+{summaries["KR"]["delta"]:,}억 (+{summaries["KR"]["pct"]}%)'),

        # KR MAU
        ('4,396</td><td class="num dn">4,242</td><td class="num dn">3,768</td><td class="num dn">3,632</td><td class="num col26 up">3,680',
         f'{Q1["KR"][2022]["mau"]:,}</td><td class="num dn">{Q1["KR"][2023]["mau"]:,}</td><td class="num dn">{Q1["KR"][2024]["mau"]:,}</td><td class="num dn">{Q1["KR"][2025]["mau"]:,}</td><td class="num col26 dn">{Q1["KR"][2026]["mau"]:,}'),
        ('4,135 → 3,642', f'{avg_pre({yr: Q1["KR"][yr]["mau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["KR"][yr]["mau"] for yr in [2025,2026]}):,}'),

        # KR ARPMAU
        ('8,859</td><td class="num up">9,620</td><td class="num up">12,129</td><td class="num up">13,452</td><td class="num col26 dn">11,300',
         f'{Q1["KR"][2022]["arpmau"]:,}</td><td class="num up">{Q1["KR"][2023]["arpmau"]:,}</td><td class="num up">{Q1["KR"][2024]["arpmau"]:,}</td><td class="num up">{Q1["KR"][2025]["arpmau"]:,}</td><td class="num col26 dn">{Q1["KR"][2026]["arpmau"]:,}'),
        ('10,203 → 13,022', f'{avg_pre({yr: Q1["KR"][yr]["arpmau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["KR"][yr]["arpmau"] for yr in [2025,2026]}):,}'),

        # ===== JP panel =====
        ('9,909</td><td class="num dn">9,297</td><td class="num up">9,375</td><td class="num dn">9,273</td><td class="num col26 dn">8,815',
         f'{Q1["JP"][2022]["rev"]:,}</td><td class="num dn">{Q1["JP"][2023]["rev"]:,}</td><td class="num up">{Q1["JP"][2024]["rev"]:,}</td><td class="num dn">{Q1["JP"][2025]["rev"]:,}</td><td class="num col26 dn">{Q1["JP"][2026]["rev"]:,}'),
        ('9,527 → 9,181', f'{summaries["JP"]["pre"]:,} → {summaries["JP"]["post"]:,}'),
        ('-346억 (-4%)', f'{summaries["JP"]["delta"]:,}억 ({summaries["JP"]["pct"]}%)'),

        # JP MAU
        ('10,114</td><td class="num dn">9,493</td><td class="num dn">8,484</td><td class="num up">8,582</td><td class="num col26 dn">8,456',
         f'{Q1["JP"][2022]["mau"]:,}</td><td class="num dn">{Q1["JP"][2023]["mau"]:,}</td><td class="num dn">{Q1["JP"][2024]["mau"]:,}</td><td class="num up">{Q1["JP"][2025]["mau"]:,}</td><td class="num col26 dn">{Q1["JP"][2026]["mau"]:,}'),
        ('9,364 → 8,557', f'{avg_pre({yr: Q1["JP"][yr]["mau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["JP"][yr]["mau"] for yr in [2025,2026]}):,}'),

        # JP ARPMAU
        ('9,798</td><td class="num">9,794</td><td class="num up">11,050</td><td class="num dn">10,804</td><td class="num col26 dn">10,424',
         f'{Q1["JP"][2022]["arpmau"]:,}</td><td class="num">{Q1["JP"][2023]["arpmau"]:,}</td><td class="num up">{Q1["JP"][2024]["arpmau"]:,}</td><td class="num dn">{Q1["JP"][2025]["arpmau"]:,}</td><td class="num col26 dn">{Q1["JP"][2026]["arpmau"]:,}'),
        ('10,214 → 10,728', f'{avg_pre({yr: Q1["JP"][yr]["arpmau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["JP"][yr]["arpmau"] for yr in [2025,2026]}):,}'),

        # ===== US panel =====
        ('15,180</td><td class="num up">16,816</td><td class="num up">19,832</td><td class="num up">20,461</td><td class="num col26 dn">19,213',
         f'{Q1["US"][2022]["rev"]:,}</td><td class="num up">{Q1["US"][2023]["rev"]:,}</td><td class="num up">{Q1["US"][2024]["rev"]:,}</td><td class="num up">{Q1["US"][2025]["rev"]:,}</td><td class="num col26 dn">{Q1["US"][2026]["rev"]:,}'),
        ('17,276 → 20,211', f'{summaries["US"]["pre"]:,} → {summaries["US"]["post"]:,}'),
        ('+2,935억 (+17%)', f'+{summaries["US"]["delta"]:,}억 (+{summaries["US"]["pct"]}%)'),

        # US MAU
        ('28,587</td><td class="num dn">27,783</td><td class="num up">28,394</td><td class="num dn">27,753</td><td class="num col26 dn">26,050',
         f'{Q1["US"][2022]["mau"]:,}</td><td class="num dn">{Q1["US"][2023]["mau"]:,}</td><td class="num up">{Q1["US"][2024]["mau"]:,}</td><td class="num dn">{Q1["US"][2025]["mau"]:,}</td><td class="num col26 up">{Q1["US"][2026]["mau"]:,}'),
        ('28,255 → 27,412', f'{avg_pre({yr: Q1["US"][yr]["mau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["US"][yr]["mau"] for yr in [2025,2026]}):,}'),

        # US ARPMAU
        ('5,310</td><td class="num up">6,053</td><td class="num up">6,985</td><td class="num up">7,373</td><td class="num col26">7,375',
         f'{Q1["US"][2022]["arpmau"]:,}</td><td class="num up">{Q1["US"][2023]["arpmau"]:,}</td><td class="num up">{Q1["US"][2024]["arpmau"]:,}</td><td class="num up">{Q1["US"][2025]["arpmau"]:,}</td><td class="num col26 dn">{Q1["US"][2026]["arpmau"]:,}'),
        ('6,116 → 7,373', f'{avg_pre({yr: Q1["US"][yr]["arpmau"] for yr in [2022,2023,2024]}):,} → {avg_post({yr: Q1["US"][yr]["arpmau"] for yr in [2025,2026]}):,}'),
    ]

    # Apply replacements
    for old, new in replacements:
        if old in html:
            html = html.replace(old, new, 1)
            print(f"  OK: {old[:50]}...")
        else:
            print(f"  MISS: {old[:50]}...")

    # --- F) Replace KR DL values ---
    kr_dl_vals = [Q1['KR'][yr]['dl'] for yr in [2022,2023,2024,2025,2026]]
    kr_dl_old = ['600', '591', '649', '568', '513']
    kr_dl_new = [str(v) for v in kr_dl_vals]
    # Replace DL text labels in SVG (KR section)
    for old_v, new_v in zip(kr_dl_old, kr_dl_new):
        # Be careful with context-specific replacements
        pass

    # --- G) Replace JP DL values ---
    jp_dl_vals = [Q1['JP'][yr]['dl'] for yr in [2022,2023,2024,2025,2026]]

    # --- H) Replace US DL values ---
    us_dl_vals = [Q1['US'][yr]['dl'] for yr in [2022,2023,2024,2025,2026]]
    us_dl_old = ['2,971', '3,126', '3,215', '3,216', '3,215']
    us_dl_new = [f'{v:,}' for v in us_dl_vals]

    # --- I) Update analysis basis info text ---
    html = html.replace(
        'iOS+Android 각각 TOP100',
        'iOS+Android 합산 TOP100'
    )
    html = html.replace(
        '3국(KR+JP+US) TOP100 앱 합산',
        '3국(KR+JP+US) iOS+Android 합산 TOP100'
    )
    # Update game count from 300 to 100 per country
    html = html.replace('300게임</span></td>', '100게임</span></td>')
    html = html.replace('100게임</span></td>', '100게임</span></td>')

    # --- J) Update 분석 기준 box ---
    old_basis = 'TOP100 매출 기준'
    new_basis = 'iOS+Android 합산 매출 TOP100 기준'
    html = html.replace(old_basis, new_basis)

    print(f"\n{'='*60}")
    print(f"HTML updated successfully!")
    print(f"Output: {OUT_PATH}")
    print(f"{'='*60}")

    write_html(html)

if __name__ == '__main__':
    main()
