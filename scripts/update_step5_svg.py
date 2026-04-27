#!/usr/bin/env python3
"""
Update NHN_market_analysis.html:
1. Replace Step 5 tables in KR, JP, US panels with new data (in_revenue_top100_unified_os=true filter)
2. Update SVG sparkline charts for MAU and DL trends
"""
import re

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# ============================================================
# SVG CHART DATA
# ============================================================
svg_data = {
    # ALL panel
    'all-mau': {'values': [45029, 43072, 41694, 42033, 42436], 'grad_id': 'all-mau-grad', 'stroke': '#64748b', 'fill_color': '#64748b', 'dot_color': '#64748b', 'show_labels': False},
    'all-dl':  {'values': [4279, 4467, 4574, 4440, 4420], 'grad_id': 'all-dl-grad', 'stroke': '#64748b', 'fill_color': '#64748b', 'dot_color': '#64748b', 'show_labels': True},
    # KR panel
    'kr-mau':  {'values': [4291, 4090, 3661, 3619, 3599], 'grad_id': 'kr-mau-grad', 'stroke': '#f59e0b', 'fill_color': '#f59e0b', 'dot_color': '#3b82f6', 'show_labels': False},
    'kr-dl':   {'values': [569, 557, 620, 549, 497], 'grad_id': 'kr-dl-grad', 'stroke': '#3b82f6', 'fill_color': '#3b82f6', 'dot_color': '#3b82f6', 'show_labels': True},
    # JP panel
    'jp-mau':  {'values': [10158, 9588, 8647, 8716, 8466], 'grad_id': 'jp-mau-grad', 'stroke': '#f59e0b', 'fill_color': '#f59e0b', 'dot_color': '#ef4444', 'show_labels': False},
    'jp-dl':   {'values': [757, 851, 802, 716, 726], 'grad_id': 'jp-dl-grad', 'stroke': '#3b82f6', 'fill_color': '#3b82f6', 'dot_color': '#ef4444', 'show_labels': True},
    # US panel
    'us-mau':  {'values': [30580, 29394, 29386, 29698, 30371], 'grad_id': 'us-mau-grad', 'stroke': '#f59e0b', 'fill_color': '#f59e0b', 'dot_color': '#a855f7', 'show_labels': False},
    'us-dl':   {'values': [2953, 3059, 3152, 3175, 3197], 'grad_id': 'us-dl-grad', 'stroke': '#3b82f6', 'fill_color': '#3b82f6', 'dot_color': '#a855f7', 'show_labels': True},
}

def calc_y(values):
    """Calculate y coords: y = 60 - (value - min) / (max - min) * 50"""
    mn, mx = min(values), max(values)
    if mx == mn:
        return [35.0] * 5
    return [round(60 - (v - mn) / (mx - mn) * 50, 1) for v in values]

def build_svg(key, data):
    """Build SVG inner content (everything between <svg> and </svg>)"""
    values = data['values']
    ys = calc_y(values)
    xs = [20, 85, 150, 215, 280]
    grad_id = data['grad_id']
    stroke = data['stroke']
    dot_color = data['dot_color']
    show_labels = data['show_labels']

    points_str = ' '.join(f"{xs[i]},{ys[i]}" for i in range(5))
    polygon_points = points_str + f" {xs[4]},68 {xs[0]},68"

    parts = []
    # gradient
    parts.append(f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{stroke}" stop-opacity="0.4"/><stop offset="100%" stop-color="{stroke}" stop-opacity="0"/></linearGradient></defs>')
    # polygon
    parts.append(f'<polygon fill="url(#{grad_id})" points="{polygon_points}"/>')
    # polyline
    parts.append(f'<polyline fill="none" stroke="{stroke}" stroke-width="2.5" points="{points_str}"/>')
    # circles
    circles = ''
    for i in range(4):
        circles += f'<circle cx="{xs[i]}" cy="{ys[i]}" r="4" fill="{dot_color}"/>'
    circles += f'<circle cx="{xs[4]}" cy="{ys[4]}" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>'
    parts.append(circles)

    # value labels (only for DL charts)
    if show_labels:
        for i in range(5):
            label_y = ys[i] - 5
            val_str = f"{values[i]:,}"
            fill = '#94a3b8'
            fw = '600'
            parts.append(f'<text x="{xs[i]}" y="{label_y}" text-anchor="middle" style="font-size:7px;fill:{fill};font-weight:{fw};font-family:Pretendard,-apple-system,sans-serif;">{val_str}</text>')

    # year labels
    years = ["'22", "'23", "'24", "'25"]
    for i, yr in enumerate(years):
        parts.append(f'<text x="{xs[i]}" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">{yr}</text>')
    # 26.1Q label
    yr_color = '#f59e0b' if 'mau' in key else '#f59e0b'
    if key.startswith('all'):
        yr_color = '#f59e0b'
    parts.append(f'<text x="{xs[4]}" y="78" text-anchor="middle" style="font-size:8px;fill:{yr_color};font-weight:700;font-family:Pretendard,-apple-system,sans-serif;">26.1Q</text>')

    return '\n        '.join(parts)


# ============================================================
# DL description text updates
# ============================================================
dl_desc = {
    'all': "22년 4,279만건 → 25년 4,440만건 → 26.1Q 4,420만건 (25년 전후: 전 4,440만 → 후 4,430만, 0%)",
    'kr':  "22년 569만건 → 25년 549만건 → 26.1Q 497만건 (25년 전후: 전 582만 → 후 539만, -7%)",
    'jp':  "22년 757만건 → 25년 716만건 → 26.1Q 726만건 (25년 전후: 전 803만 → 후 718만, -11%)",
    'us':  "22년 2,953만건 → 25년 3,175만건 → 26.1Q 3,197만건 (25년 전후: 전 3,055만 → 후 3,180만, +4%)",
}


# ============================================================
# STEP 5 DATA
# ============================================================

def game_row(name, y22, y23, y24, y25, y26, pre, post, delta, is_up=True):
    """Generate a table row for a game"""
    sign = '+' if delta > 0 else ''
    cls = 'up' if delta > 0 else 'dn'
    return f'          <tr><td>{name}</td><td class="num">{y22}</td><td class="num">{y23}</td><td class="num">{y24}</td><td class="num">{y25}</td><td class="num col26">{y26}</td><td class="num">{pre} → {post}</td><td class="num {cls}">{sign}{delta}억</td></tr>'

def tot_row(label, y22, y23, y24, y25, y26, delta, is_up=True):
    if isinstance(delta, str):
        # Already formatted like "+1,220"
        cls = 'up' if delta.startswith('+') else 'dn'
        return f'          <tr class="tot"><td>{label}</td><td class="num">{y22}</td><td class="num">{y23}</td><td class="num">{y24}</td><td class="num">{y25}</td><td class="num">{y26}</td><td class="num">-</td><td class="num {cls}">{delta}억</td></tr>'
    cls = 'up' if delta > 0 else 'dn'
    sign = '+' if delta > 0 else ''
    return f'          <tr class="tot"><td>{label}</td><td class="num">{y22}</td><td class="num">{y23}</td><td class="num">{y24}</td><td class="num">{y25}</td><td class="num">{y26}</td><td class="num">-</td><td class="num {cls}">{sign}{delta}억</td></tr>'

def table_header():
    return """        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>"""


# ---- KR STEP 5 ----
kr_step5_body = """
      <h4 style="font-size:0.82rem;margin-top:16px;color:#f59e0b;">🇨🇳 중화권 퍼블리셔 <span style="font-size:0.7rem;color:#64748b;font-weight:400;">— Survival 메가히트 (Step 4 중화권 × Strategy 주도)</span></h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 5 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Whiteout Survival", 0, 94, 215, 381, 243, 103, 353, 250),
    game_row("Last War:Survival Game", 0, 32, 332, 276, 214, 121, 264, 143),
    game_row("Kingshot", 0, 0, 0, 99, 137, 0, 107, 107),
    game_row("Last Z: Survival Shooter", 0, 0, 0, 86, 102, 0, 89, 89),
    game_row("I9: 인페르노 나인", 0, 0, 0, 70, 28, 0, 62, 62),
    tot_row("증가 TOP 5 합계", 0, 126, 547, 912, 724, 651),
]) + """
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 3 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Genshin Impact", 93, 93, 53, 34, 35, 80, 34, -46, False),
    game_row("아르케랜드", 105, 32, 0, 0, 0, 46, 0, -46, False),
    game_row("히어로즈 테일즈", 85, 26, 10, 0, 0, 40, 0, -40, False),
    tot_row("감소 TOP 3 합계", 283, 151, 63, 34, 35, -132, False),
]) + """
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#3b82f6;">🇰🇷 KR 퍼블리셔 <span style="font-size:0.7rem;color:#64748b;font-weight:400;">— RPG 내부 교체 (Step 4 KR × RPG 분해)</span></h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 신작 RPG 4종 진입 (25년 런칭)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("MapleStory: Idle RPG", 0, 0, 0, 604, 487, 0, 581, 581),
    game_row("뱀피르", 0, 0, 0, 348, 44, 0, 287, 287),
    game_row("Seven Knights Re:BIRTH", 0, 0, 0, 215, 36, 0, 179, 179),
    game_row("마비노기 모바일", 0, 0, 0, 197, 79, 0, 173, 173),
    tot_row("증가 TOP 4 합계", 0, 0, 0, "1,364", 646, "+1,220", True),
]) + """
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 기존 RPG 노후작 TOP 5 (동반 하락)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Lineage W", 350, 144, 106, 67, 25, 200, 59, -141, False),
    game_row("오딘: 발할라 라이징", 297, 237, 201, 135, 73, 245, 123, -122, False),
    game_row("나이트 크로우", 0, 244, 50, 21, 12, 98, 19, -79, False),
    game_row("리니지2M", 147, 131, 98, 59, 23, 125, 52, -73, False),
    game_row("리니지M", 398, 464, 497, 435, 187, 453, 385, -68, False),
    tot_row("감소 TOP 5 합계", "1,192", "1,220", 952, 717, 320, -483, False),
]) + """
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#64748b;">🌐 기타 (글로벌) 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 1 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Royal Match", 13, 51, 129, 123, 96, 64, 118, 54),
    tot_row("증가 합계", 13, 51, 129, 123, 96, 54),
]) + """
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#a855f7;">🇺🇸 북미 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 1 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Roblox", 67, 70, 73, 117, 91, 70, 112, 42),
    tot_row("증가 합계", 67, 70, 73, 117, 91, 42),
]) + """
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> Step 4 장르 변화를 게임 단위로 풀면 두 가지 스토리가 보임 — (1) <strong>중화권 Survival 3종(Whiteout +250·Last War +143·Kingshot +107)이 독립 +500억대 메가 성장</strong>으로 시장 견인 (2) <strong>KR RPG는 내부 교체 진행 중</strong> — 25년 신작 4종(MapleStory Idle +581·뱀피르 +287·세븐나이츠 RE:BIRTH +179·마비노기 +173) +1,220억이 기존 리니지 시리즈·오딘 등 -483억대 노후화를 압도 → 그러나 신작의 26.1Q 급락(뱀피르 348→44, SK RE:BIRTH 215→36)이 지속성 리스크.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 각 퍼블리셔 국적별로 <strong>25년 전후 월평균 매출 변화액 TOP 게임</strong> (증가/감소 각각)<br>
        • <strong>전 = 22~24 36개월 평균 / 후 = 25~26.1Q 15개월 평균</strong><br>
        • FUNFLY = 중화권 강제 분류 적용<br>
        • <strong>in_revenue_top100_unified_os = true</strong> 필터 적용 (iOS+Android 통합 매출 TOP100)<br>
        • 매출: revenue_usd_100p × 연도별 평균환율 (22:1292, 23:1307, 24:1364, 25:1422, 26:1409)<br>
        • 전 또는 후 월평균 5억 이상 조합만, 변화량 절대값 내림차순 정렬
      </div>"""


# ---- JP STEP 5 ----
jp_step5_body = """
      <h4 style="font-size:0.82rem;margin-top:16px;color:#ef4444;">🇯🇵 JP 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 5 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("SDガンダム ジージェネレーション エターナル", 0, 0, 0, 324, 179, 0, 295, 295),
    game_row("Pokémon TCG Pocket", 0, 0, 504, 343, 186, 168, 312, 144),
    game_row("Shadowverse: Worlds Beyond", 0, 0, 0, 160, 67, 0, 141, 141),
    game_row("学園アイドルマスター", 0, 0, 243, 184, 86, 81, 164, 83),
    game_row("eFootball", 58, 173, 225, 235, 228, 152, 234, 82),
    tot_row("증가 TOP 5 합계", 58, 173, 972, "1,246", 746, 745),
]) + """
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 7 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("モンスターストライク", 748, 640, 559, 398, 355, 649, 389, -260, False),
    game_row("ウマ娘 プリティーダービー", 747, 482, 345, 273, 337, 525, 286, -239, False),
    game_row("Fate/Grand Order", 562, 466, 383, 397, 255, 470, 369, -101, False),
    game_row("プロ野球スピリッツＡ", 331, 324, 237, 185, 253, 297, 199, -98, False),
    game_row("プロジェクトセカイ", 193, 163, 124, 80, 57, 160, 75, -85, False),
    game_row("ヘブンバーンズレッド", 189, 131, 104, 59, 43, 141, 56, -85, False),
    game_row("パズル＆ドラゴンズ", 292, 229, 207, 150, 205, 243, 161, -82, False),
    tot_row("감소 TOP 7 합계", "3,062", "2,435", "1,959", "1,542", "1,505", -950, False),
]) + """
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#f59e0b;">🇨🇳 중화권 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 6 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Whiteout Survival", 0, 44, 139, 278, 288, 61, 280, 219),
    game_row("Last War:Survival", 0, 0, 191, 276, 239, 64, 269, 205),
    game_row("Last War:Survival Game", 0, 0, 105, 194, 194, 35, 194, 159),
    game_row("Wuthering Waves", 0, 0, 63, 105, 130, 21, 110, 89),
    game_row("Kingshot", 0, 0, 0, 77, 101, 0, 82, 82),
    game_row("Last Z: Survival Shooter", 0, 0, 0, 78, 85, 0, 79, 79),
    tot_row("증가 TOP 6 합계", 0, 44, 498, "1,008", "1,037", 833),
]) + """
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 4 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("GODDESS OF VICTORY: NIKKE", 611, 249, 173, 135, 117, 344, 131, -213, False),
    game_row("Genshin Impact", 363, 257, 206, 144, 179, 275, 151, -124, False),
    game_row("ドット勇者", 0, 183, 61, 29, 0, 81, 23, -58, False),
    game_row("あんさんぶるスターズ", 171, 143, 116, 101, 97, 143, 100, -43, False),
    tot_row("감소 TOP 4 합계", "1,145", 832, 556, 409, 393, -438, False),
]) + """
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#64748b;">🌐 기타 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 4 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Royal Match", 30, 103, 178, 161, 138, 104, 156, 52),
    game_row("杖と剣の伝説", 0, 0, 0, 56, 31, 0, 51, 51),
    game_row("Disney Solitaire", 0, 0, 0, 46, 57, 0, 48, 48),
    game_row("Toon Blast", 58, 50, 83, 106, 112, 64, 107, 43),
    tot_row("증가 TOP 4 합계", 88, 153, 261, 369, 338, 194),
]) + """
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> 25년 전후로 <strong>JP 신작 SDガンダム +295·Pokémon TCG Pocket +144·Shadowverse +141·学園アイマス +83·eFootball +82 = JP 퍼블 +745억</strong> 신규 IP 메가 성장. <strong>중화권 Whiteout +219 + Last War 2종 합 +364 + Wuthering Waves +89 + Kingshot +82 + Last Z +79 = 중화권 +833억</strong> 추가 성장. 동시에 <strong>モンスト -260·ウマ娘 -239·FGO -101·プロスピA -98 등 JP 전통 IP -950억대 노후화</strong> — 신규(+745)가 노후화(-950)를 완전 상쇄 못해 JP 퍼블 순감소.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 각 퍼블리셔 국적별로 <strong>25년 전후 월평균 매출 변화액 TOP 게임</strong> (증가/감소 각각)<br>
        • <strong>전 = 22~24 36개월 평균 / 후 = 25~26.1Q 15개월 평균</strong><br>
        • FUNFLY = 중화권 강제 분류 적용<br>
        • <strong>in_revenue_top100_unified_os = true</strong> 필터 적용 (iOS+Android 통합 매출 TOP100)<br>
        • 변화 절대값 30억 이상 게임만 표시
      </div>"""


# ---- US STEP 5 ----
us_step5_body = """
      <h4 style="font-size:0.82rem;margin-top:16px;color:#f59e0b;">🇨🇳 중화권 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 6 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Last War:Survival", 0, 0, 409, 724, 731, 136, 725, 589),
    game_row("Kingshot", 0, 0, 0, 491, 614, 0, 516, 516),
    game_row("Whiteout Survival", 0, 204, 533, 602, 508, 246, 583, 337),
    game_row("Last War:Survival Game", 0, 0, 222, 383, 393, 74, 385, 311),
    game_row("Gossip Harbor Merge", 0, 41, 89, 268, 476, 43, 310, 267),
    game_row("Last Z: Survival Shooter", 0, 0, 0, 223, 392, 0, 257, 257),
    tot_row("증가 TOP 6 합계", 0, 245, "1,253", "2,691", "3,114", "+2,277", True),
]) + """
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 4 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Top War", 147, 130, 76, 34, 0, 118, 27, -91, False),
    game_row("Last Shelter", 104, 92, 49, 0, 0, 82, 0, -82, False),
    game_row("Genshin Impact", 279, 159, 107, 96, 125, 182, 102, -80, False),
    game_row("Puzzles & Survival", 212, 189, 153, 129, 85, 185, 120, -65, False),
    tot_row("감소 TOP 4 합계", 742, 570, 385, 259, 210, -318, False),
]) + """
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#64748b;">🌐 기타 (글로벌) 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 5 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Royal Kingdom", 0, 0, 79, 342, 446, 26, 363, 337),
    game_row("Royal Match", 430, 950, "1,352", "1,227", "1,088", 911, "1,199", 288),
    game_row("Clash Royale", 161, 117, 159, 435, 222, 146, 392, 246),
    game_row("Match Factory", 0, 63, 205, 275, 258, 89, 272, 183),
    game_row("Disney Solitaire", 0, 0, 0, 133, 169, 0, 140, 140),
    tot_row("증가 TOP 5 합계", 591, "1,130", "1,795", "2,412", "2,183", "+1,194", True),
]) + """
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 3 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("State of Survival", 241, 149, 79, 56, 0, 156, 45, -111, False),
    game_row("Clash of Clans", 359, 319, 329, 267, 181, 336, 250, -86, False),
    game_row("Solitaire Grand Harvest", 170, 214, 202, 141, 76, 195, 128, -67, False),
    tot_row("감소 TOP 3 합계", 770, 682, 610, 464, 257, -264, False),
]) + """
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#a855f7;">🇺🇸 북미 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 2 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("MONOPOLY GO!", 0, "1,680", "2,267", "1,793", "1,483", "1,316", "1,731", 415),
    game_row("Umamusume (JP)", 0, 0, 0, 163, 80, 0, 146, 146),
    tot_row("증가 TOP 2 합계", 0, "1,680", "2,267", "1,956", "1,563", 561),
]) + """
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 3 (25년 전후 월평균)</div>
      <table>
""" + table_header() + """
        <tbody>
""" + '\n'.join([
    game_row("Roblox", 739, 903, "1,151", 422, 158, 931, 369, -562, False),
    game_row("Star Trek Fleet Command", 126, 83, 63, 0, 0, 91, 0, -91, False),
    game_row("Diablo Immortal", 171, 55, 41, 0, 36, 89, 7, -82, False),
    tot_row("감소 TOP 3 합계", "1,036", "1,041", "1,255", 422, 194, -735, False),
]) + """
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> 25년 전후로 미국 시장은 <strong>중화권 Survival 4종(Last War +589·Kingshot +516·Whiteout +337·Last War SG +311) + Gossip Harbor +267 + Last Z +257 = 중화권 +2,277억 메가 성장</strong>이 시장의 핵심 엔진. 기타에서 <strong>Royal Kingdom +337·Royal Match +288·Clash Royale +246·Match Factory +183·Disney Solitaire +140 = +1,194억</strong> 동반 폭발. 북미는 MONOPOLY GO +415 + Umamusume +146 = +561억이나 Roblox -562·Star Trek -91·Diablo -82 = -735억으로 순 손실.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 각 퍼블리셔 국적별로 <strong>25년 전후 월평균 매출 변화액 TOP 게임</strong> (증가/감소 각각)<br>
        • <strong>전 = 22~24 36개월 평균 / 후 = 25~26.1Q 15개월 평균</strong><br>
        • FUNFLY = 중화권 강제 분류 적용<br>
        • <strong>in_revenue_top100_unified_os = true</strong> 필터 적용 (iOS+Android 통합 매출 TOP100)<br>
        • 변화 절대값 50억 이상 게임만 표시
      </div>"""


# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    changes = []

    # ---- 1. UPDATE SVG CHARTS ----
    # Strategy: Find each SVG by its gradient ID, then replace the entire SVG content

    for key, data in svg_data.items():
        grad_id = data['grad_id']
        # Find the SVG that contains this gradient
        pattern = re.compile(
            r'(<svg viewBox="0 0 300 80"[^>]*>)\s*(.*?)\s*(</svg>)',
            re.DOTALL
        )
        new_inner = '\n        ' + build_svg(key, data) + '\n      '

        # Find the specific SVG containing this grad_id
        found = False
        for m in pattern.finditer(html):
            if grad_id in m.group(2):
                old_full = m.group(0)
                new_full = m.group(1) + new_inner + m.group(3)
                html = html.replace(old_full, new_full, 1)
                found = True
                changes.append(f"Updated SVG chart: {key}")
                break
        if not found:
            print(f"WARNING: Could not find SVG with gradient {grad_id}")

    # ---- 2. UPDATE DL DESCRIPTION TEXT ----
    # KR DL desc
    old_kr_dl_desc = '22년 600만건 → 25년 568만건 → 26.1Q 513만건 (25년 전후: 전 613만 → 후 557만, -9%)'
    html = html.replace(old_kr_dl_desc, dl_desc['kr'], 1)
    changes.append("Updated KR DL description text")

    old_jp_dl_desc = '22년 766만건 → 25년 719만건 → 26.1Q 725만건 (25년 전후: 전 812만 → 후 720만, -11%)'
    html = html.replace(old_jp_dl_desc, dl_desc['jp'], 1)
    changes.append("Updated JP DL description text")

    old_us_dl_desc = '22년 2,971만건 → 25년 3,216만건 → 26.1Q 3,215만건 (25년 전후: 전 3,104만 → 후 3,216만, +4%)'
    html = html.replace(old_us_dl_desc, dl_desc['us'], 1)
    changes.append("Updated US DL description text")

    old_all_dl_desc = '22년 4,338만건 → 25년 4,503만건 → 26.1Q 4,454만건 (25년 전후: 전 4,529만 → 후 4,493만, -1%)'
    html = html.replace(old_all_dl_desc, dl_desc['all'], 1)
    changes.append("Updated ALL DL description text")

    # ---- 3. UPDATE STEP 5 SECTIONS ----

    # KR Step 5: Find from "<!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->" in KR panel
    # to the closing </div></div> before "<!-- 한국 퍼블리셔 TOP10"
    # The KR step 5 is the first occurrence

    # Find KR Step 5 body content (between <div class="step-body"> and closing </div>)
    # Strategy: find the first Step 5 comment, then replace the step-body content

    # KR STEP 5
    kr_step5_marker_start = '대표 게임별 증감 — Step 4 장르 변화의 실체'
    kr_step5_end_marker = '<!-- 한국 퍼블리셔 TOP10'

    idx_start = html.find(kr_step5_marker_start)
    if idx_start >= 0:
        # Find the step-body after this
        body_start_tag = '<div class="step-body">'
        body_start = html.find(body_start_tag, idx_start)
        if body_start >= 0:
            body_content_start = body_start + len(body_start_tag)
            # Find the end: look for the closing pattern before the next section
            end_idx = html.find(kr_step5_end_marker, body_content_start)
            if end_idx >= 0:
                # Go back to find </div>\n  </div>\n\n before the end marker
                # The step-body ends with </div>\n  </div>\n\n
                search_back = html[body_content_start:end_idx]
                # Find last </div> pair
                last_close = search_back.rfind('</div>')
                second_last = search_back.rfind('</div>', 0, last_close)
                if second_last >= 0:
                    old_body = html[body_content_start:body_content_start + second_last]
                    html = html[:body_content_start] + kr_step5_body + html[body_content_start + second_last:]
                    changes.append("Replaced KR Step 5 body content")

    # Also update KR Step 5 summary line
    old_kr_summary = '(1) <strong>중화권 × Strategy +579억</strong>의 실체 = Whiteout·Last War·Kingshot 등 Survival 메가히트 동반 폭발 &nbsp;|&nbsp; (2) <strong>KR × RPG -178억</strong>의 실체 = 25년 신작 4종(MapleStory Idle·마비노기 등) <span class="up">+572억</span>이 기존 리니지·오딘 <span class="dn">-750억대</span>를 부분 상쇄한 결과'
    new_kr_summary = '(1) <strong>중화권 Survival +651억</strong>의 실체 = Whiteout +250·Last War +143·Kingshot +107 등 메가히트 동반 폭발 &nbsp;|&nbsp; (2) <strong>KR RPG 내부 교체</strong> = 25년 신작 4종(MapleStory Idle +581·뱀피르 +287 등) <span class="up">+1,220억</span>이 기존 리니지·오딘 <span class="dn">-483억</span>을 압도하나 26.1Q 급락 리스크'
    html = html.replace(old_kr_summary, new_kr_summary, 1)
    changes.append("Updated KR Step 5 summary line")

    # JP STEP 5
    jp_step5_marker = '퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)'
    # Find all occurrences - the 1st is JP, 2nd is US
    jp_idx = html.find(jp_step5_marker)
    if jp_idx >= 0:
        body_start_tag = '<div class="step-body">'
        body_start = html.find(body_start_tag, jp_idx)
        if body_start >= 0:
            body_content_start = body_start + len(body_start_tag)
            # Find end: next "<!-- " or conclusion div
            # JP step 5 ends before the JP conclusion
            jp_conclusion = html.find('<div class="conclusion jp">', body_content_start)
            if jp_conclusion >= 0:
                search_back = html[body_content_start:jp_conclusion]
                last_close = search_back.rfind('</div>')
                second_last = search_back.rfind('</div>', 0, last_close)
                if second_last >= 0:
                    html = html[:body_content_start] + jp_step5_body + html[body_content_start + second_last:]
                    changes.append("Replaced JP Step 5 body content")

    # Update JP Step 5 summary
    old_jp_summary = 'Pokémon TCG Pocket <span class="up">+270억</span> · SDガンダム <span class="up">+230억</span> · 중화권 Whiteout/Last War 합 <span class="up">+592억</span> 신규 메가 | モンスト <span class="dn">-260억</span> · ウマ娘 <span class="dn">-239억</span> · FGO <span class="dn">-101억</span> 노후화'
    new_jp_summary = 'SDガンダム <span class="up">+295억</span> · Pokémon TCG Pocket <span class="up">+144억</span> · Shadowverse <span class="up">+141억</span> · 중화권 Whiteout/Last War 합 <span class="up">+583억</span> 신규 메가 | モンスト <span class="dn">-260억</span> · ウマ娘 <span class="dn">-239억</span> · NIKKE <span class="dn">-213억</span> 노후화'
    html = html.replace(old_jp_summary, new_jp_summary, 1)
    changes.append("Updated JP Step 5 summary line")

    # US STEP 5
    us_step5_marker = '퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)'
    # After JP replacement, the US one is the remaining occurrence
    us_idx = html.find(us_step5_marker)
    if us_idx >= 0:
        body_start_tag = '<div class="step-body">'
        body_start = html.find(body_start_tag, us_idx)
        if body_start >= 0:
            body_content_start = body_start + len(body_start_tag)
            us_conclusion = html.find('<div class="conclusion us">', body_content_start)
            if us_conclusion >= 0:
                search_back = html[body_content_start:us_conclusion]
                last_close = search_back.rfind('</div>')
                second_last = search_back.rfind('</div>', 0, last_close)
                if second_last >= 0:
                    html = html[:body_content_start] + us_step5_body + html[body_content_start + second_last:]
                    changes.append("Replaced US Step 5 body content")

    # Update US Step 5 summary
    old_us_summary = '중화권 Survival 4종(Last War +589·Kingshot +417·Whiteout +360·Last War SG +310) <span class="up">+1,676억</span> 메가 | MONOPOLY GO <span class="up">+602억</span> | 기타 Royal Kingdom +361·Royal Match +288·Clash Royale +246 동반 폭발 | Roblox <span class="dn">-561억</span> 단독 노후화'
    new_us_summary = '중화권 Survival 4종(Last War +589·Kingshot +516·Whiteout +337·Last War SG +311) <span class="up">+2,277억</span> 메가 | MONOPOLY GO <span class="up">+415억</span> | 기타 Royal Kingdom +337·Royal Match +288·Clash Royale +246 동반 폭발 | Roblox <span class="dn">-562억</span> 단독 노후화'
    html = html.replace(old_us_summary, new_us_summary, 1)
    changes.append("Updated US Step 5 summary line")

    # ---- WRITE BACK ----
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("=" * 60)
    print("UPDATE COMPLETE")
    print("=" * 60)
    for c in changes:
        print(f"  [OK] {c}")
    print(f"\nTotal changes: {len(changes)}")

if __name__ == '__main__':
    main()
