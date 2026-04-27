#!/usr/bin/env python3
"""
Step 3 (장르별 매출) & Step 4 (퍼블국적×장르) 테이블 업데이트
- Role Playing → MMORPG / 비MMORPG RPG 분리
- 모든 데이터 새 수치로 교체
"""
import re, math

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

def fmt(v):
    """억원 포맷: 1000 이상이면 콤마"""
    if v == 0:
        return "0"
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    return f"{v:.0f}"

def fmt_delta(d):
    if d > 0:
        return f"+{fmt(d)}"
    elif d < 0:
        return f"-{fmt(abs(d))}"
    return "0"

def calc_pre_post(y22, y23, y24, y25, y26):
    pre = (y22 + y23 + y24) / 3
    post = (y25 * 12 + y26 * 3) / 15
    delta = post - pre
    if pre != 0:
        pct = (post - pre) / pre * 100
    else:
        pct = float('inf')
    return round(pre), round(post), round(delta), pct

def up_dn(val, prev=None, delta=None):
    """CSS class: up/dn based on context"""
    if delta is not None:
        return "up" if delta > 0 else ("dn" if delta < 0 else "")
    if prev is not None:
        return "up" if val > prev else ("dn" if val < prev else "")
    return ""

def make_genre_row(name, vals, bold=False, is_last_col_26=True):
    """Build a single genre table row with 5 year values + pre/post change col."""
    y22, y23, y24, y25, y26 = vals
    pre, post, delta, pct = calc_pre_post(y22, y23, y24, y25, y26)

    name_td = f"<strong>{name}</strong>" if bold else name

    # year-over-year up/dn
    classes = ["", "", "", "", ""]
    prev_vals = [None, y22, y23, y24, y25]
    for i in range(1, 5):
        if vals[i] > prev_vals[i]:
            classes[i] = " up"
        elif vals[i] < prev_vals[i]:
            classes[i] = " dn"

    col26_cls = " col26" + classes[4]
    classes[4] = col26_cls

    # last column
    delta_cls = "up" if delta > 0 else ("dn" if delta < 0 else "")
    if pct == float('inf'):
        pct_str = "New"
    else:
        pct_str = f"{pct:+.0f}%"

    if delta > 0:
        color = "#059669"
    elif delta < 0:
        color = "#dc2626"
    else:
        color = "#64748b"

    change_td = (
        f'<strong>{fmt(pre)} → {fmt(post)}</strong><br>'
        f'{fmt_delta(delta)}억 (<span style="color:{color};font-weight:700;">{pct_str}</span>)'
    )

    tds = []
    tds.append(f'<td>{name_td}</td>')
    for i, v in enumerate(vals):
        tds.append(f'<td class="num{classes[i]}">{fmt(v)}</td>')
    tds.append(f'<td class="num {delta_cls}">{change_td}</td>')

    return "          <tr>" + "".join(tds) + "</tr>"


def make_total_row(vals, delta_val=None):
    y22, y23, y24, y25, y26 = vals
    pre, post, delta, pct = calc_pre_post(y22, y23, y24, y25, y26)
    tds = ['<td>합계</td>']
    for i, v in enumerate(vals):
        cls = " col26" if i == 4 else ""
        tds.append(f'<td class="num{cls}">{fmt(v)}</td>')
    tds.append(f'<td class="num">{fmt_delta(delta)}억</td>')
    return '          <tr class="tot">' + "".join(tds) + "</tr>"


# ===================== DATA =====================

# --- KR Step 3 ---
kr_step3 = [
    ("Strategy", [318, 390, 874, 1192, 1019], True),
    ("MMORPG", [1957, 1890, 1495, 1340, 643], True),
    ("비MMORPG RPG", [614, 646, 725, 878, 981], True),
    ("Puzzle", [111, 180, 306, 390, 434], False),
    ("Casino", [81, 86, 86, 92, 111], False),
    ("Sports", [191, 239, 205, 202, 194], False),
    ("Adventure", [204, 188, 180, 187, 183], False),
    ("Action", [153, 128, 244, 157, 117], False),
    ("Casual", [5, 75, 128, 134, 139], False),
    ("Card", [44, 43, 46, 56, 73], False),
    ("Simulation", [54, 62, 35, 64, 93], False),
    ("Board", [12, 18, 25, 25, 26], False),
    ("Arcade", [42, 39, 123, 62, 38], False),
]

# --- JP Step 3 ---
jp_step3 = [
    ("비MMORPG RPG", [3312, 3241, 2948, 2374, 2046], True),
    ("Strategy", [876, 664, 1042, 1525, 1551], True),
    ("Adventure", [1765, 1309, 1082, 900, 819], False),
    ("Action", [992, 905, 997, 900, 906], False),
    ("Puzzle", [864, 919, 945, 963, 1165], False),
    ("Arcade", [109, 108, 374, 667, 476], True),
    ("Sports", [527, 650, 571, 523, 549], False),
    ("Music", [493, 405, 298, 196, 153], False),
    ("Simulation", [375, 512, 602, 653, 625], False),
    ("Card", [145, 184, 182, 227, 222], False),
    ("MMORPG", [166, 91, 54, 61, 19], True),
    ("Board", [54, 52, 49, 50, 45], False),
    ("Casual", [30, 30, 43, 19, 35], False),
]

# --- US Step 3 ---
us_step3 = [
    ("Puzzle", [3327, 4170, 4865, 5569, 5930], True),
    ("Casino", [2546, 2582, 2426, 2154, 1716], True),
    ("Strategy", [2212, 2002, 2677, 3816, 3765], True),
    ("비MMORPG RPG", [1516, 1260, 1045, 991, 717], False),
    ("Adventure", [1373, 1465, 1807, 1405, 1160], False),
    ("Action", [1035, 1008, 950, 877, 776], False),
    ("Board", [328, 1512, 2800, 2204, 1780], False),
    ("Casual", [621, 656, 580, 575, 733], False),
    ("Card", [468, 504, 481, 476, 386], False),
    ("Arcade", [472, 426, 943, 994, 837], False),
    ("Simulation", [386, 380, 369, 526, 531], False),
    ("Sports", [178, 176, 162, 164, 149], False),
    ("MMORPG", [52, 0, 0, 0, 0], True),
]


# --- KR Step 4 Increase ---
kr_step4_inc = [
    ("중화권", "#f59e0b", "Strategy", [228, 304, 778, 1054, 860]),
    ("KR", "#3b82f6", "비MMORPG RPG", [318, 220, 185, 554, 732]),
    ("중화권", "#f59e0b", "Puzzle", [12, 16, 46, 122, 183]),
    ("기타", "#64748b", "Puzzle", [103, 176, 260, 268, 251]),
    ("KR", "#3b82f6", "Casual", [5, 75, 87, 101, 97]),
    ("북미", "#a855f7", "Adventure", [92, 83, 81, 127, 113]),
    ("KR", "#3b82f6", "Strategy", [19, 22, 36, 57, 91]),
    ("중화권", "#f59e0b", "Casual", [0, 12, 38, 32, 42]),
]

kr_step4_dec = [
    ("KR", "#3b82f6", "MMORPG", [1730, 1700, 1423, 1220, 570]),
    ("중화권", "#f59e0b", "비MMORPG RPG", [244, 400, 514, 314, 242]),
    ("중화권", "#f59e0b", "MMORPG", [220, 186, 70, 117, 73]),
    ("KR", "#3b82f6", "Adventure", [89, 80, 39, 28, 17]),
    ("KR", "#3b82f6", "Sports", [189, 235, 189, 178, 177]),
    ("기타", "#64748b", "Arcade", [37, 38, 108, 41, 34]),
    ("중화권", "#f59e0b", "Action", [80, 68, 93, 65, 49]),
]


def sort_by_delta(data_list):
    """Sort by delta descending (for increases) or ascending (for decreases)."""
    result = []
    for item in data_list:
        vals = item[-1]  # last element is the vals list
        _, _, delta, _ = calc_pre_post(*vals)
        result.append((delta, item))
    result.sort(key=lambda x: -x[0])
    return [item for _, item in result]


def sort_genre_by_delta_desc(genre_list):
    """Sort genres by delta descending for display."""
    result = []
    for name, vals, bold in genre_list:
        _, _, delta, _ = calc_pre_post(*vals)
        result.append((delta, (name, vals, bold)))
    result.sort(key=lambda x: -x[0])
    return [item for _, item in result]


def build_step3_tbody(genre_list):
    """Build full tbody content for Step 3 genre table, sorted by delta desc."""
    sorted_genres = sort_genre_by_delta_desc(genre_list)
    rows = []
    totals = [0, 0, 0, 0, 0]
    for name, vals, bold in sorted_genres:
        rows.append(make_genre_row(name, vals, bold=bold))
        for i in range(5):
            totals[i] += vals[i]
    rows.append(make_total_row(totals))
    return "\n".join(rows)


def build_step3_summary(genre_list, market="KR"):
    """Build step-a summary text for Step 3."""
    items = []
    for name, vals, bold in genre_list:
        pre, post, delta, pct = calc_pre_post(*vals)
        items.append((name, pre, post, delta, pct))

    # Sort by delta desc
    items.sort(key=lambda x: -x[3])

    ups = [(n, d, p) for n, _, _, d, p in items if d > 0]
    dns = [(n, d, p) for n, _, _, d, p in items if d < 0]

    parts = []
    for n, d, p in ups[:4]:
        pct_s = f"+{p:.0f}%" if p != float('inf') else "New"
        parts.append(f'{n} <span class="up">{fmt_delta(d)}억 ({pct_s})</span>')
    up_str = " · ".join(parts)

    parts2 = []
    for n, d, p in dns[:3]:
        parts2.append(f'{n} <span class="dn">{fmt_delta(d)}억 ({p:+.0f}%)</span>')
    dn_str = " · ".join(parts2)

    return f"{up_str} 성장 | {dn_str} 하락"


def make_step4_row(pub_name, pub_color, genre_name, vals):
    y22, y23, y24, y25, y26 = vals
    pre, post, delta, pct = calc_pre_post(y22, y23, y24, y25, y26)

    pub_span = f'<span style="color:{pub_color};">{pub_name}</span>'
    name_td = f'{pub_span} × <strong>{genre_name}</strong>'

    tds = [f'<td>{name_td}</td>']
    for i, v in enumerate(vals):
        cls = " col26" if i == 4 else ""
        tds.append(f'<td class="num{cls}">{fmt(v)}</td>')

    delta_cls = "up" if delta > 0 else "dn"
    pre_post_str = f'{fmt(pre)} → {fmt(post)}'
    pct_str = f"{pct:+.0f}%" if pct != float('inf') else "New"
    change_html = f'<strong>{pre_post_str}</strong><br>{fmt_delta(delta)}억 ({pct_str})'
    tds.append(f'<td class="num {delta_cls}">{change_html}</td>')

    return "          <tr>" + "".join(tds) + "</tr>"


def make_step4_total_row(label, items):
    totals = [0, 0, 0, 0, 0]
    for pub, color, genre, vals in items:
        for i in range(5):
            totals[i] += vals[i]
    pre, post, delta, pct = calc_pre_post(*totals)
    delta_cls = "up" if delta > 0 else "dn"
    tds = [f'<td>{label}</td>']
    for i, v in enumerate(totals):
        cls = " col26" if i == 4 else ""
        tds.append(f'<td class="num{cls}">{fmt(v)}</td>')
    tds.append(f'<td class="num {delta_cls}">{fmt_delta(delta)}억</td>')
    return '          <tr class="tot">' + "".join(tds) + "</tr>"


def build_step4_table(items, is_increase=True):
    rows = []
    for pub, color, genre, vals in items:
        rows.append(make_step4_row(pub, color, genre, vals))
    label = f"TOP {len(items)} {'증가' if is_increase else '감소'} 합계"
    rows.append(make_step4_total_row(label, items))
    return "\n".join(rows)


def build_step4_summary():
    """Build KR Step 4 step-a summary."""
    # Top increases
    inc_parts = []
    for pub, color, genre, vals in kr_step4_inc[:3]:
        _, _, delta, _ = calc_pre_post(*vals)
        pub_span = f'<span style="color:{color};">{pub}</span>'
        inc_parts.append(f'{pub_span} {genre} <span class="up">{fmt_delta(delta)}억</span>')

    # Top decrease
    dec_parts = []
    for pub, color, genre, vals in kr_step4_dec[:2]:
        _, _, delta, _ = calc_pre_post(*vals)
        pub_span = f'<span style="color:{color};">{pub}</span>'
        dec_parts.append(f'{pub_span} {genre} <span class="dn">{fmt_delta(delta)}억</span>')

    return " · ".join(inc_parts) + " 성장 | " + " · ".join(dec_parts) + " 하락"


# ===================== MAIN =====================

def main():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # ============ KR Step 3 ============
    # Find the KR Step 3 tbody (line ~1815-1828)
    # Pattern: after "장르별 월평균 매출 변화</div>" in KR panel, find <tbody>...</tbody>
    kr_step3_start = html.find('<div class="ctab-panel" id="kr">')
    kr_step3_marker = html.find('장르별 월평균 매출 변화</div>', kr_step3_start)

    # Find the tbody after this marker
    tbody_start = html.find('<tbody>', kr_step3_marker)
    tbody_end = html.find('</tbody>', tbody_start) + len('</tbody>')
    old_kr_tbody = html[tbody_start:tbody_end]
    new_kr_tbody = "<tbody>\n" + build_step3_tbody(kr_step3) + "\n        </tbody>"
    html = html[:tbody_start] + new_kr_tbody + html[tbody_end:]

    # Update KR Step 3 step-a summary
    kr_step3_stepa_start = html.find('장르별 월평균 매출 변화</div>', kr_step3_start)
    stepa_start = html.find('<div class="step-a">', kr_step3_stepa_start)
    stepa_end = html.find('</div>', stepa_start) + len('</div>')
    old_stepa = html[stepa_start:stepa_end]
    new_stepa_content = build_step3_summary(kr_step3, "KR")
    new_stepa = f'<div class="step-a">{new_stepa_content}</div>'
    html = html[:stepa_start] + new_stepa + html[stepa_end:]

    # Update KR Step 3 insight text
    kr_ins_marker = html.find('장르별 월평균 매출 변화</div>', kr_step3_start)
    ins_start = html.find('<div class="ins">', kr_ins_marker)
    ins_end = html.find('</div>', ins_start) + len('</div>')
    # Calculate key deltas
    mmorpg_pre, mmorpg_post, mmorpg_delta, mmorpg_pct = calc_pre_post(*dict((n, v) for n, v, _ in kr_step3)["MMORPG"])
    nonmmo_pre, nonmmo_post, nonmmo_delta, nonmmo_pct = calc_pre_post(*dict((n, v) for n, v, _ in kr_step3)["비MMORPG RPG"])
    strat_pre, strat_post, strat_delta, strat_pct = calc_pre_post(*dict((n, v) for n, v, _ in kr_step3)["Strategy"])
    new_ins = (
        '<div class="ins"><strong>핵심:</strong> 25년 전후로 <strong>Strategy '
        f'{fmt_delta(strat_delta)}억({strat_pct:+.0f}%)</strong> 단독 메가 성장. '
        f'비MMORPG RPG {fmt_delta(nonmmo_delta)}억({nonmmo_pct:+.0f}%) · Puzzle 성장 동반. '
        f'반면 <strong>MMORPG {fmt_delta(mmorpg_delta)}억({mmorpg_pct:+.0f}%)</strong> 대폭 감소 — '
        f'RPG 내에서도 MMORPG 하락 vs 비MMORPG 성장의 양극화 뚜렷. '
        f'<strong>"MMORPG 쇠퇴 + 비MMORPG RPG·Strategy·Puzzle 부상의 장르 대전환기"</strong>.</div>'
    )
    html = html[:ins_start] + new_ins + html[ins_end:]

    # ============ JP Step 3 ============
    jp_panel_start = html.find('<div class="ctab-panel" id="jp">')
    jp_step3_marker = html.find('장르별 월평균 매출 변화</div>', jp_panel_start)

    # Find JP Step 3 tbody
    jp_tbody_start = html.find('<tbody>', jp_step3_marker)
    jp_tbody_end = html.find('</tbody>', jp_tbody_start) + len('</tbody>')
    new_jp_tbody = "<tbody>\n" + build_step3_tbody(jp_step3) + "\n        </tbody>"
    html = html[:jp_tbody_start] + new_jp_tbody + html[jp_tbody_end:]

    # Update JP Step 3 step-a
    jp_stepa_start = html.find('<div class="step-a">', jp_step3_marker)
    jp_stepa_end = html.find('</div>', jp_stepa_start) + len('</div>')
    new_jp_stepa_content = build_step3_summary(jp_step3, "JP")
    new_jp_stepa = f'<div class="step-a">{new_jp_stepa_content}</div>'
    html = html[:jp_stepa_start] + new_jp_stepa + html[jp_stepa_end:]

    # Update JP Step 3 insight
    jp_ins_start = html.find('<div class="ins">', jp_step3_marker)
    jp_ins_end = html.find('</div>', jp_ins_start) + len('</div>')
    jp_mmorpg_pre, jp_mmorpg_post, jp_mmorpg_delta, jp_mmorpg_pct = calc_pre_post(*dict((n, v) for n, v, _ in jp_step3)["MMORPG"])
    jp_nonmmo_pre, jp_nonmmo_post, jp_nonmmo_delta, jp_nonmmo_pct = calc_pre_post(*dict((n, v) for n, v, _ in jp_step3)["비MMORPG RPG"])
    jp_strat_pre, jp_strat_post, jp_strat_delta, jp_strat_pct = calc_pre_post(*dict((n, v) for n, v, _ in jp_step3)["Strategy"])
    jp_adv_pre, jp_adv_post, jp_adv_delta, jp_adv_pct = calc_pre_post(*dict((n, v) for n, v, _ in jp_step3)["Adventure"])
    new_jp_ins = (
        f'<div class="ins"><strong>핵심:</strong> JP는 25년 전후로 '
        f'<strong>비MMORPG RPG {fmt_delta(jp_nonmmo_delta)}억({jp_nonmmo_pct:+.0f}%) + Adventure {fmt_delta(jp_adv_delta)}억({jp_adv_pct:+.0f}%) 노후화</strong>가 시장 하락 주도. '
        f'MMORPG는 {fmt_delta(jp_mmorpg_delta)}억으로 원래 비중 작아 영향 미미. '
        f'반면 <strong>Strategy {fmt_delta(jp_strat_delta)}억(중화권 Survival) + Arcade·Simulation·Puzzle 성장</strong>이 부분 상쇄 — '
        f'신구 교체 진행 중인 정체 시장.</div>'
    )
    html = html[:jp_ins_start] + new_jp_ins + html[jp_ins_end:]

    # ============ US Step 3 ============
    us_panel_start = html.find('<div class="ctab-panel" id="us">')
    us_step3_marker = html.find('장르별 월평균 매출 변화</div>', us_panel_start)

    us_tbody_start = html.find('<tbody>', us_step3_marker)
    us_tbody_end = html.find('</tbody>', us_tbody_start) + len('</tbody>')
    new_us_tbody = "<tbody>\n" + build_step3_tbody(us_step3) + "\n        </tbody>"
    html = html[:us_tbody_start] + new_us_tbody + html[us_tbody_end:]

    # Update US Step 3 step-a
    us_stepa_start = html.find('<div class="step-a">', us_step3_marker)
    us_stepa_end = html.find('</div>', us_stepa_start) + len('</div>')
    new_us_stepa_content = build_step3_summary(us_step3, "US")
    new_us_stepa = f'<div class="step-a">{new_us_stepa_content}</div>'
    html = html[:us_stepa_start] + new_us_stepa + html[us_stepa_end:]

    # Update US Step 3 insight
    us_ins_start = html.find('<div class="ins">', us_step3_marker)
    us_ins_end = html.find('</div>', us_ins_start) + len('</div>')
    us_mmorpg_pre, us_mmorpg_post, us_mmorpg_delta, us_mmorpg_pct = calc_pre_post(*dict((n, v) for n, v, _ in us_step3)["MMORPG"])
    us_nonmmo_pre, us_nonmmo_post, us_nonmmo_delta, us_nonmmo_pct = calc_pre_post(*dict((n, v) for n, v, _ in us_step3)["비MMORPG RPG"])
    us_strat_pre, us_strat_post, us_strat_delta, us_strat_pct = calc_pre_post(*dict((n, v) for n, v, _ in us_step3)["Strategy"])
    us_puzzle_pre, us_puzzle_post, us_puzzle_delta, us_puzzle_pct = calc_pre_post(*dict((n, v) for n, v, _ in us_step3)["Puzzle"])
    us_casino_pre, us_casino_post, us_casino_delta, us_casino_pct = calc_pre_post(*dict((n, v) for n, v, _ in us_step3)["Casino"])
    new_us_ins = (
        f'<div class="ins"><strong>핵심:</strong> 25년 전후로 미국은 '
        f'<strong>Puzzle {fmt_delta(us_puzzle_delta)}억({us_puzzle_pct:+.0f}%) + Strategy {fmt_delta(us_strat_delta)}억({us_strat_pct:+.0f}%)</strong> 양대 메가 견인. '
        f'Board·Arcade·Simulation 동반 폭발. '
        f'반면 Casino {fmt_delta(us_casino_delta)}억·비MMORPG RPG {fmt_delta(us_nonmmo_delta)}억 노후화 — '
        f'MMORPG는 22년 {fmt(us_mmorpg_pre)}억 이후 시장에서 사실상 퇴출. '
        f'<strong>"Puzzle·Strategy 양강 + Board 신흥이 Casino·RPG 하락을 압도하며 +17% 성장"</strong>.</div>'
    )
    html = html[:us_ins_start] + new_us_ins + html[us_ins_end:]

    # ============ KR Step 4 ============
    kr_step4_marker = html.find('퍼블리셔 국적 × 장르 매출 변화', kr_step3_start)

    # Update KR Step 4 step-a
    kr_s4_stepa_start = html.find('<div class="step-a">', kr_step4_marker)
    kr_s4_stepa_end = html.find('</div>', kr_s4_stepa_start) + len('</div>')
    new_s4_stepa = f'<div class="step-a">{build_step4_summary()}</div>'
    html = html[:kr_s4_stepa_start] + new_s4_stepa + html[kr_s4_stepa_end:]

    # Update increase table tbody
    inc_h4_marker = html.find('▲ 증가 Top 조합', kr_step4_marker)
    inc_tbody_start = html.find('<tbody>', inc_h4_marker)
    inc_tbody_end = html.find('</tbody>', inc_tbody_start) + len('</tbody>')
    new_inc_tbody = "<tbody>\n" + build_step4_table(kr_step4_inc, True) + "\n        </tbody>"
    html = html[:inc_tbody_start] + new_inc_tbody + html[inc_tbody_end:]

    # Update decrease table tbody
    dec_h4_marker = html.find('▼ 감소 Top 조합', kr_step4_marker)
    dec_tbody_start = html.find('<tbody>', dec_h4_marker)
    dec_tbody_end = html.find('</tbody>', dec_tbody_start) + len('</tbody>')
    new_dec_tbody = "<tbody>\n" + build_step4_table(kr_step4_dec, False) + "\n        </tbody>"
    html = html[:dec_tbody_start] + new_dec_tbody + html[dec_tbody_end:]

    # Update KR Step 4 insight
    kr_s4_ins_start = html.find('<div class="ins">', dec_h4_marker)
    kr_s4_ins_end = html.find('</div>', kr_s4_ins_start) + len('</div>')
    kr_mmorpg_kr_delta = calc_pre_post(*kr_step4_dec[0][-1])[2]
    kr_nonmmo_kr_delta = calc_pre_post(*kr_step4_inc[1][-1])[2]
    kr_strat_cn_delta = calc_pre_post(*kr_step4_inc[0][-1])[2]
    new_s4_ins = (
        f'<div class="ins"><strong>핵심:</strong> 25년 전후로 <strong>중화권 Strategy 단독 {fmt_delta(kr_strat_cn_delta)}억</strong>이 시장 성장의 핵심 동력. '
        f'<strong>KR 비MMORPG RPG {fmt_delta(kr_nonmmo_kr_delta)}억</strong> 급부상이 RPG 내 세대 교체를 증명. '
        f'반면 <strong>KR MMORPG {fmt_delta(kr_mmorpg_kr_delta)}억</strong>은 리니지·오딘 등 '
        f'MMORPG 노후화가 본격화 — 구체적으로 어떤 게임이 오르고 내렸는지는 <strong>Step 5</strong>에서 바로 이어짐.</div>'
    )
    html = html[:kr_s4_ins_start] + new_s4_ins + html[kr_s4_ins_end:]

    # ============ Also update 3국 합산 Step 3 ============
    # The global Step 3 is before KR panel. We need to update its "Role Playing" row too.
    # Find it: it's at line ~1650, before id="kr"
    global_step3_marker = html.find('장르별 월평균 매출 변화 <span')
    if global_step3_marker != -1 and global_step3_marker < html.find('<div class="ctab-panel" id="kr">'):
        # Find and replace the "Role Playing" row in the global table
        global_tbody_start = html.find('<tbody>', global_step3_marker)
        global_tbody_end = html.find('</tbody>', global_tbody_start) + len('</tbody>')
        old_global_tbody = html[global_tbody_start:global_tbody_end]

        # Replace "Role Playing" row with MMORPG + 비MMORPG RPG rows
        kr_d = {n: v for n, v, _ in kr_step3}
        jp_d = {n: v for n, v, _ in jp_step3}
        us_d = {n: v for n, v, _ in us_step3}

        mmorpg_combined = [kr_d["MMORPG"][i] + jp_d["MMORPG"][i] + us_d["MMORPG"][i] for i in range(5)]
        nonmmo_combined = [kr_d["비MMORPG RPG"][i] + jp_d["비MMORPG RPG"][i] + us_d["비MMORPG RPG"][i] for i in range(5)]

        # Find the Role Playing row in old_global_tbody and replace
        rp_row_start = old_global_tbody.find('Role Playing')
        if rp_row_start != -1:
            # Find the <tr> that contains it
            tr_start = old_global_tbody.rfind('<tr', 0, rp_row_start)
            tr_end = old_global_tbody.find('</tr>', rp_row_start) + len('</tr>')
            old_rp_row = old_global_tbody[tr_start:tr_end]
            new_rp_rows = make_genre_row("MMORPG", mmorpg_combined, bold=True) + "\n" + make_genre_row("비MMORPG RPG", nonmmo_combined, bold=True)
            new_global_tbody = old_global_tbody[:tr_start] + new_rp_rows + old_global_tbody[tr_end:]

            # Update total row
            # Recalculate totals since we split RPG
            html = html[:global_tbody_start] + new_global_tbody + html[global_tbody_end:]

            # Update step-a for global Step 3
            global_stepa_start = html.find('<div class="step-a">', global_step3_marker)
            global_stepa_end = html.find('</div>', global_stepa_start) + len('</div>')

            gm_pre, gm_post, gm_delta, gm_pct = calc_pre_post(*mmorpg_combined)
            gnm_pre, gnm_post, gnm_delta, gnm_pct = calc_pre_post(*nonmmo_combined)
            new_global_stepa = (
                f'<div class="step-a">Strategy <span class="up">+74%</span> · Arcade <span class="up">+88%</span> · Board <span class="up">+35%</span> · Puzzle <span class="up">+34%</span> 급성장 | '
                f'MMORPG <span class="dn">{gm_pct:+.0f}%</span> · Adventure <span class="dn">-22%</span> · Music <span class="dn">-54%</span> 하락 (비MMORPG RPG <span class="dn">{gnm_pct:+.0f}%</span>)</div>'
            )
            html = html[:global_stepa_start] + new_global_stepa + html[global_stepa_end:]

            # Update global insight
            global_ins_start = html.find('<div class="ins">', global_step3_marker)
            global_ins_end = html.find('</div>', global_ins_start) + len('</div>')
            new_global_ins = (
                f'<div class="ins"><strong>핵심:</strong> Strategy와 Puzzle이 성장의 양대 축. Arcade·Board도 고성장 장르. '
                f'반면 <strong>MMORPG({fmt_delta(gm_delta)}억, {gm_pct:+.0f}%)</strong>가 최대 감소 — 3국 모두 MMORPG 매출 후퇴 공통. '
                f'비MMORPG RPG는 {fmt_delta(gnm_delta)}억({gnm_pct:+.0f}%)으로 상대적으로 선방. '
                f'<strong>"MMORPG 쇠퇴 속 비MMORPG RPG 선방 + Strategy·Puzzle 대체하는 장르 대전환기"</strong>.</div>'
            )
            html = html[:global_ins_start] + new_global_ins + html[global_ins_end:]

    # ============ Verify div balance ============
    div_open = html.count('<div')
    div_close = html.count('</div>')
    print(f"<div count: {div_open}, </div> count: {div_close}")
    if div_open != div_close:
        print(f"WARNING: div mismatch! diff={div_open - div_close}")
    else:
        print("OK: div tags balanced")

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("Done! HTML updated successfully.")


# Helper to get data dicts for global step 3
kr_step3_data = [(n, v) for n, v, _ in kr_step3]
jp_step3_data = [(n, v) for n, v, _ in jp_step3]
us_step3_data = [(n, v) for n, v, _ in us_step3]


if __name__ == "__main__":
    main()
