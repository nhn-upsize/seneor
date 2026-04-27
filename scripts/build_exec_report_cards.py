# -*- coding: utf-8 -*-
"""임원 보고용 리포트 v2 — 근거에 표/차트 시각화 통합"""
import os

OUT = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_exec_report_cards.html"

# ============================================================
# 차트 빌더 헬퍼
# ============================================================
def bar_compare(rows, title='', unit='억', max_val=None, accent=None):
    """
    rows: [(label, value, color, sub_label), ...]
    다이버징 수평 막대 (0축 기준 양수 오른쪽 / 음수 왼쪽)
    음수가 있으면 자동으로 다이버징 레이아웃, 없으면 일반 좌측 정렬
    """
    if not rows: return ''
    has_negative = any(r[1] < 0 for r in rows)
    has_positive = any(r[1] > 0 for r in rows)
    max_v = max_val or max(abs(r[1]) for r in rows) * 1.25
    n = len(rows)
    row_h = 38
    title_h = 30 if title else 0
    tick_h = 20 if (has_positive and has_negative) else 10
    pad_top = title_h + tick_h
    pad_bot = 14
    total_w = 680
    label_w = 140
    value_w = 90
    bar_area_total = total_w - label_w - value_w
    svg_h = pad_top + n * row_h + pad_bot

    # 축 위치
    if has_negative and has_positive:
        max_neg = max((abs(r[1]) for r in rows if r[1] < 0), default=0)
        max_pos = max((r[1] for r in rows if r[1] > 0), default=0)
        ratio = max_neg / (max_neg + max_pos) if (max_neg + max_pos) else 0.3
        axis_x = label_w + bar_area_total * ratio
    elif has_negative:
        # 전부 음수 — 축을 오른쪽에
        axis_x = label_w + bar_area_total
    else:
        # 전부 양수 — 축을 왼쪽에
        axis_x = label_w

    svg = [f'<svg viewBox="0 0 {total_w} {svg_h}" style="width:100%;max-width:780px;height:auto;display:block;margin:8px 0;">']
    if title:
        svg.append(f'<text x="{total_w/2}" y="18" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">{title}</text>')

    tick_y = pad_top - 6
    # 0 축 (세로선)
    svg.append(f'<line x1="{axis_x}" y1="{pad_top-2}" x2="{axis_x}" y2="{svg_h-pad_bot+2}" stroke="#cbd5e1" stroke-width="1.5"/>')
    # 0 라벨 — 양쪽 다 있을 때만 의미있음
    if has_positive and has_negative:
        svg.append(f'<text x="{axis_x}" y="{tick_y}" text-anchor="middle" font-size="9" fill="#94a3b8">0</text>')

    # 양수쪽 눈금
    if has_positive:
        pos_px = (total_w - value_w) - axis_x
        if pos_px > 20:
            for frac in [0.5, 1.0]:
                gx = axis_x + pos_px * frac
                gv = max_v * frac
                svg.append(f'<line x1="{gx}" y1="{pad_top-2}" x2="{gx}" y2="{svg_h-pad_bot+2}" stroke="#f1f5f9" stroke-dasharray="2,3"/>')
                if frac == 1.0:
                    svg.append(f'<text x="{gx}" y="{tick_y}" text-anchor="middle" font-size="9" fill="#cbd5e1">+{int(gv)}</text>')
    # 음수쪽 눈금
    if has_negative:
        neg_px = axis_x - label_w
        if neg_px > 20:
            for frac in [0.5, 1.0]:
                gx = axis_x - neg_px * frac
                gv = max_v * frac
                svg.append(f'<line x1="{gx}" y1="{pad_top-2}" x2="{gx}" y2="{svg_h-pad_bot+2}" stroke="#f1f5f9" stroke-dasharray="2,3"/>')
                if frac == 1.0:
                    svg.append(f'<text x="{gx}" y="{tick_y}" text-anchor="middle" font-size="9" fill="#cbd5e1">-{int(gv)}</text>')

    for i, row in enumerate(rows):
        label = row[0]; val = row[1]
        color = row[2] if len(row) > 2 else ('#059669' if val >= 0 else '#dc2626')
        sub = row[3] if len(row) > 3 else ''
        y = pad_top + i * row_h + 12
        bar_h = 22

        # label (좌측 이름)
        lbl_color = color if val != 0 else '#64748b'
        svg.append(f'<text x="{label_w - 10}" y="{y+bar_h/2+4}" text-anchor="end" font-size="12" fill="#1e293b" font-weight="700">{label}</text>')

        # bar
        if val >= 0:
            w = val / max_v * pos_px
            bar_x = axis_x
            val_x = bar_x + w + 8
            val_anchor = 'start'
        else:
            w = abs(val) / max_v * (axis_x - label_w)
            bar_x = axis_x - w
            val_x = bar_x - 8
            val_anchor = 'end'

        # 그라데이션 효과
        svg.append(f'<rect x="{bar_x}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="{color}" rx="3" opacity="0.9"/>')

        # 값 라벨
        val_txt = f'+{val:,.0f}{unit}' if val > 0 else f'{val:,.0f}{unit}'
        svg.append(f'<text x="{val_x}" y="{y+bar_h/2+5}" text-anchor="{val_anchor}" font-size="12" fill="{color}" font-weight="800">{val_txt}</text>')

        # sub 라벨 (아래쪽)
        if sub:
            sub_color = '#94a3b8'
            if '+' in sub or '%' in sub and val > 0: sub_color = '#059669'
            elif '-' in sub or '⚠' in sub: sub_color = '#dc2626'
            svg.append(f'<text x="{val_x}" y="{y+bar_h/2+19}" text-anchor="{val_anchor}" font-size="10" fill="{sub_color}" font-weight="600">{sub}</text>')

    svg.append('</svg>')
    return ''.join(svg)

def before_after_bars(rows, title='', unit='억'):
    """
    rows: [(label, before, after, color), ...]
    전/후 duo 바
    """
    if not rows: return ''
    max_v = max(max(r[1], r[2]) for r in rows) * 1.15
    n = len(rows)
    row_h = 44
    title_h = 24 if title else 0
    legend_h = 18
    pad_top = title_h + legend_h + 8
    pad_bot = 14
    total_w = 620; label_w = 160
    bar_area = total_w - label_w - 110
    svg_h = pad_top + n * row_h + pad_bot

    svg = [f'<svg viewBox="0 0 {total_w} {svg_h}" style="width:100%;max-width:740px;height:auto;display:block;margin:8px 0;">']
    if title:
        svg.append(f'<text x="{total_w/2}" y="18" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">{title}</text>')
    # 범례 (제목 아래 별도 줄)
    legend_y = title_h + 10
    svg.append(f'<rect x="{label_w}" y="{legend_y-7}" width="10" height="8" fill="#cbd5e1"/>')
    svg.append(f'<text x="{label_w+14}" y="{legend_y}" font-size="10" fill="#64748b">전 (22~24)</text>')
    svg.append(f'<rect x="{label_w+90}" y="{legend_y-7}" width="10" height="8" fill="#3b82f6"/>')
    svg.append(f'<text x="{label_w+104}" y="{legend_y}" font-size="10" fill="#64748b">후 (25~26.1Q)</text>')

    for i, (label, b, a, color) in enumerate(rows):
        y = pad_top + i * row_h
        b_w = b / max_v * bar_area
        a_w = a / max_v * bar_area
        svg.append(f'<text x="{label_w - 8}" y="{y+14}" text-anchor="end" font-size="11" fill="#1e293b" font-weight="600">{label}</text>')
        # 전
        svg.append(f'<rect x="{label_w}" y="{y}" width="{b_w:.1f}" height="12" fill="#cbd5e1" rx="1"/>')
        svg.append(f'<text x="{label_w + b_w + 4}" y="{y+10}" font-size="10" fill="#64748b">{b:,.0f}{unit}</text>')
        # 후
        svg.append(f'<rect x="{label_w}" y="{y+14}" width="{a_w:.1f}" height="12" fill="{color}" rx="1"/>')
        svg.append(f'<text x="{label_w + a_w + 4}" y="{y+24}" font-size="10" fill="{color}" font-weight="700">{a:,.0f}{unit}</text>')
        # delta
        diff = a - b
        pct = (diff/b*100) if b else 0
        dcolor = '#059669' if diff > 0 else '#dc2626'
        svg.append(f'<text x="{total_w - 8}" y="{y+17}" text-anchor="end" font-size="10" fill="{dcolor}" font-weight="700">{diff:+,.0f} ({pct:+.0f}%)</text>')
    svg.append('</svg>')
    return ''.join(svg)

def line_chart(series_data, x_labels, title='', y_max=None, unit='%'):
    """
    series_data: [{'name':'KR','color':'#3b82f6','values':[...]}]
    x_labels: ['2022','2023',...]
    """
    W = 600; H = 240
    left, right, top, bot = 60, 500, 50, 195
    all_vals = [v for s in series_data for v in s['values']]
    ymax = y_max or max(all_vals) * 1.2
    xs = [left + i*((right-left)/(len(x_labels)-1)) for i in range(len(x_labels))]

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:720px;height:auto;display:block;margin:8px 0;">']
    if title:
        svg.append(f'<text x="{W/2}" y="22" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">{title}</text>')

    # grid
    for gi in range(5):
        gv = ymax * gi / 4
        y = bot - (bot-top) * gi / 4
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{gv:.0f}{unit}</text>')
    for i, lbl in enumerate(x_labels):
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+16}" text-anchor="middle" font-size="10" fill="#64748b" font-weight="600">{lbl}</text>')

    # lines
    for s in series_data:
        color = s['color']
        vals = s['values']
        pts = [(xs[i], bot - (bot-top) * vals[i] / ymax) for i in range(len(vals))]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
        svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{pts_str}"/>')
        for i, (x, y) in enumerate(pts):
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>')
        # 끝 값 라벨
        svg.append(f'<text x="{pts[-1][0]+6:.1f}" y="{pts[-1][1]+3:.1f}" font-size="10" fill="{color}" font-weight="700">{s["name"]}: {vals[-1]:.1f}{unit}</text>')

    svg.append('</svg>')
    return ''.join(svg)

def line_chart_multi(series_data, x_labels, title='', y_max=None, unit='억', y_step=None):
    """다중 라인 차트 — 각 시리즈 끝에 라벨 표시"""
    W = 720; H = 280
    left, right, top, bot = 60, 590, 55, 225
    all_vals = [v for s in series_data for v in s['values']]
    ymax = y_max or (max(all_vals) * 1.15)
    xs = [left + i*((right-left)/(len(x_labels)-1)) for i in range(len(x_labels))]
    step = y_step or (ymax // 4)

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:820px;height:auto;display:block;margin:8px 0;">']
    if title:
        svg.append(f'<text x="{(left+right)/2}" y="22" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">{title}</text>')

    # grid
    for v in range(0, int(ymax)+1, int(step)):
        y = bot - (bot-top) * v / ymax
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-4}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{v:,}{unit}</text>')
    for i, lbl in enumerate(x_labels):
        c = '#f59e0b' if '26' in lbl else '#64748b'
        w = '800' if '26' in lbl else '600'
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+18}" text-anchor="middle" font-size="10" fill="{c}" font-weight="{w}">{lbl}</text>')

    # 라인 + 마지막 값 라벨은 오른쪽 영역에
    label_offsets = []  # 라벨 겹침 방지
    for s in sorted(series_data, key=lambda x: -x['values'][-1]):
        color = s['color']
        vals = s['values']
        pts = [(xs[i], bot - (bot-top) * vals[i] / ymax) for i in range(len(vals))]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
        svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{pts_str}"/>')
        for i, (x, y) in enumerate(pts):
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>')

        # 끝점 라벨 (오른쪽)
        end_x = pts[-1][0]
        end_y = pts[-1][1]
        # 겹침 조정
        adjusted_y = end_y
        for ey in label_offsets:
            if abs(adjusted_y - ey) < 14:
                adjusted_y = ey + 14
        label_offsets.append(adjusted_y)
        svg.append(f'<text x="{end_x+8}" y="{adjusted_y+4}" font-size="11" fill="{color}" font-weight="800">{s["name"]} {vals[-1]:,.0f}</text>')

    svg.append('</svg>')
    return ''.join(svg)

def stacked_bar_yearly(series_data, x_labels, title='', unit='억'):
    """누적 바 (연도별 구성)"""
    W = 720; H = 340
    title_h = 24 if title else 0
    legend_lines = len(series_data)
    legend_h = legend_lines * 16 + 10
    left = 60
    right = 660
    top = title_h + legend_h + 20
    bot = H - 50  # X labels 영역 확보
    # 각 x 위치의 총합 구해 max 결정
    totals = []
    for i in range(len(x_labels)):
        t = sum(s['values'][i] for s in series_data)
        totals.append(t)
    ymax = max(totals) * 1.12
    xs = [left + i*((right-left)/(len(x_labels)-1)) for i in range(len(x_labels))]
    bar_w = 50

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:820px;height:auto;display:block;margin:8px 0;">']
    if title:
        svg.append(f'<text x="{(left+right)/2}" y="18" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">{title}</text>')

    # 범례 (제목 아래 별도 블록, 좌측부터 수평 or 수직)
    ly_start = title_h + 14
    for si, s in enumerate(series_data):
        lx_box = left
        lx_txt = left + 14
        ly = ly_start + si * 16
        svg.append(f'<rect x="{lx_box}" y="{ly-8}" width="10" height="10" fill="{s["color"]}" rx="1"/>')
        svg.append(f'<text x="{lx_txt}" y="{ly}" font-size="10" fill="#475569">{s["name"]}</text>')

    # grid
    step = int(ymax / 5 / 500) * 500 or 500
    for v in range(0, int(ymax)+1, step):
        y = bot - (bot-top) * v / ymax
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-4}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{v:,}{unit}</text>')

    # 막대 누적
    for i, lbl in enumerate(x_labels):
        cx = xs[i]
        cum = 0
        for s in series_data:
            val = s['values'][i]
            h = (bot-top) * val / ymax
            y0 = bot - (bot-top) * cum / ymax - h
            svg.append(f'<rect x="{cx - bar_w/2}" y="{y0:.1f}" width="{bar_w}" height="{h:.1f}" fill="{s["color"]}" opacity="0.88"/>')
            if h > 16:
                svg.append(f'<text x="{cx}" y="{y0 + h/2 + 4:.1f}" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">{val:,.0f}</text>')
            cum += val
        # 총합 라벨 (막대 위)
        top_y = bot - (bot-top) * cum / ymax
        svg.append(f'<text x="{cx}" y="{top_y - 6:.1f}" text-anchor="middle" font-size="11" fill="#1e293b" font-weight="800">{cum:,.0f}</text>')
        # X 라벨 (하단 여유)
        c = '#f59e0b' if '26' in lbl else '#64748b'
        w = '800' if '26' in lbl else '600'
        svg.append(f'<text x="{cx}" y="{bot+18}" text-anchor="middle" font-size="10" fill="{c}" font-weight="{w}">{lbl}</text>')

    svg.append('</svg>')
    return ''.join(svg)

def rank_line_chart(rank_data, x_labels, country_color='#ef4444', title=''):
    """순위별 매출 추이 라인 차트 (로그 스케일)
    rank_data: {'1위':[...], '10위':[...], ...}
    """
    import math
    W = 720; H = 300
    left, right, top, bot = 70, 620, 55, 245
    all_vals = [v for rs in rank_data.values() for v in rs]
    log_min = math.floor(math.log10(max(min(all_vals), 1)))
    log_max = math.ceil(math.log10(max(all_vals)))
    def yc(v):
        if v <= 0: return bot
        lv = math.log10(v)
        return top + (bot-top) * (1 - (lv - log_min) / (log_max - log_min))
    xs = [left + i*((right-left)/(len(x_labels)-1)) for i in range(len(x_labels))]

    # 순위별 색상 (진한 → 연한)
    rank_colors_map = {
        '#ef4444': ['#991b1b','#dc2626','#ef4444','#f87171','#fca5a5'],
        '#3b82f6': ['#1e40af','#2563eb','#3b82f6','#60a5fa','#93c5fd'],
        '#a855f7': ['#581c87','#7c3aed','#a855f7','#c084fc','#d8b4fe'],
    }
    palette = rank_colors_map.get(country_color, rank_colors_map['#ef4444'])

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:820px;height:auto;display:block;margin:8px 0;">']
    if title:
        svg.append(f'<text x="{(left+right)/2}" y="22" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">{title}</text>')

    # Y grid
    for exp in range(int(log_min), int(log_max)+1):
        v = 10**exp
        y = yc(v)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        label = f'{v:,}억' if v < 10000 else f'{v//10000:,}만억'
        svg.append(f'<text x="{left-6}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{label}</text>')

    # X labels
    for i, lbl in enumerate(x_labels):
        c = '#f59e0b' if '26' in lbl else '#64748b'
        w = '800' if '26' in lbl else '600'
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+18}" text-anchor="middle" font-size="10" fill="{c}" font-weight="{w}">{lbl}</text>')

    # 라인
    for ri, rank in enumerate(['1위','10위','20위','50위','100위']):
        rc = palette[ri]
        vals = rank_data[rank]
        pts = [(xs[i], yc(vals[i])) for i in range(len(vals))]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
        svg.append(f'<polyline fill="none" stroke="{rc}" stroke-width="2.5" points="{pts_str}"/>')
        for i, (x, y) in enumerate(pts):
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{rc}"/>')
        # 끝 라벨
        svg.append(f'<text x="{pts[-1][0]+8:.1f}" y="{pts[-1][1]+4:.1f}" font-size="11" fill="{rc}" font-weight="800">{rank} ({vals[-1]}억)</text>')

    svg.append('</svg>')
    return ''.join(svg)

def mini_table(headers, rows, accent='#0085ca'):
    """간단한 표"""
    html = '<table class="mini-table"><thead><tr>'
    for h in headers: html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for row in rows:
        html += '<tr>'
        for i, cell in enumerate(row):
            cls = ' class="num"' if i > 0 else ''
            html += f'<td{cls}>{cell}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# ============================================================
# 인사이트 (차트 포함)
# ============================================================
INSIGHTS = [
    {
        'id': 'kr-1',
        'section': 'KR',
        'headline': '한국 시장은 망한 게 아니다 — 오히려 +13% 성장 중',
        'interpretation': '겉보기 KR 퍼블 -6%만 보면 "한국이 꺼진다"로 보이지만, 실제 <strong>전체 시장은 4,109억 → 4,654억으로 +545억(+13%) 성장</strong>. KR 퍼블 감소분(-146억)보다 중화권 증가분(+568억)이 <strong>4배</strong> 큰 규모로 시장 성장을 단독 견인.',
        'chart': '',
        'evidence': [
            ('전체 시장', '4,109억 → 4,654억 (+545억, +13%)'),
            ('KR 퍼블', '2,463억 → 2,317억 (-146억, -6%)'),
            ('중화권', '1,154억 → 1,722억 (+568억, +49%)'),
            ('요점', 'KR 퍼블 감소(-146)의 <strong>4배</strong>를 중화권(+568)이 차지'),
        ],
    },
    {
        'id': 'kr-2',
        'section': 'KR',
        'headline': 'KR 퍼블 내부는 "죽은 기업" vs "성장 기업"으로 쪼개졌다',
        'interpretation': '"엔씨 1/3 토막"이라기보다 <strong>카카오게임즈가 반토막 (-57%, -214억/월)</strong>이 최대 충격. 같은 KR 퍼블 내에서도 <strong>넷마블 +94% · 넥슨 +34%</strong>로 양극화.<br><br>연도별 흐름을 보면 더 극적이다 — <strong>카카오는 365억(22)→93억(26.1Q)로 연속 하락</strong>, 반면 <strong>넥슨은 24년 253억 딥 후 26.1Q 759억으로 V자 회복</strong>. 한국 대형 퍼블 내부에서도 운명이 갈리는 중.',
        'chart': line_chart_multi([
            {'name':'넥슨',   'color':'#059669', 'values':[484, 451, 253, 473, 759]},
            {'name':'넷마블',  'color':'#10b981', 'values':[214, 197, 214, 463, 168]},
            {'name':'카카오',  'color':'#dc2626', 'values':[365, 430, 332, 180,  93]},
            {'name':'NHN',    'color':'#0085ca', 'values':[ 86, 112, 123, 129, 135]},
            {'name':'엔씨',   'color':'#f59e0b', 'values':[107,  96, 105,  89,  85]},
        ], ['2022', '2023', '2024', '2025', '26.1Q'], title='KR TOP5 퍼블리셔 연도별 월평균 매출 (억)', y_max=800, y_step=200, unit=''),
        'evidence': [
            ('넥슨', "'22 484억 → '26.1Q 759억 (+57%) · 24년 일시 급락 후 회복"),
            ('넷마블', "'22 214억 → '25 463억 피크 → '26.1Q 168억 (변동성 큼)"),
            ('카카오게임즈', "'22 365억 → '26.1Q 93억 (-74%) · 지속 하락"),
            ('엔씨', "'22 107억 → '26.1Q 85억 (-21%) · 완만한 하락"),
            ('NHN', "'22 86억 → '26.1Q 135억 (+57%) · 웹보드 강세로 안정 성장"),
            ('요점', '"한국 퍼블 감소"는 주로 <strong>카카오게임즈 단독 현상</strong>. 넥슨·NHN은 오히려 성장 중'),
        ],
    },
    {
        'id': 'kr-2b',
        'section': 'KR',
        'headline': 'TOP5보다 "그 외 한국 퍼블"이 더 많이 빠졌다',
        'interpretation': '표면적으로는 "KR 퍼블 -6%"이지만 속을 쪼개보면 더 놀라움. <strong>TOP5는 1,256→1,240억으로 거의 변화 없음(-1%)</strong>. 진짜 빠진 건 <strong>TOP5 바깥 KR 중소 퍼블 — 1,308→724억으로 거의 반토막 (-45%)</strong>.<br><br>동시에 <strong>해외 퍼블(중화권/북미/기타)은 1,271→2,107억으로 +66% 급증</strong>. 즉 한국 시장의 진짜 재편은 "TOP5 vs 중소" — <strong>중소 KR 퍼블이 해외 퍼블에게 자리를 넘기는 구도</strong>.',
        'chart': stacked_bar_yearly([
            {'name':'TOP5 (엔씨+넥슨+넷마블+카카오+NHN)', 'color':'#3b82f6', 'values':[1256, 1286, 1028, 1333, 1240]},
            {'name':'기타 KR 퍼블',                    'color':'#94a3b8', 'values':[1308, 1262, 1248, 1072,  724]},
            {'name':'해외 퍼블 (중화권/북미/기타)',          'color':'#f59e0b', 'values':[1271, 1455, 2212, 2395, 2107]},
        ], ['2022', '2023', '2024', '2025', '26.1Q'], title='KR 시장 구성 변화 — 연도별 월평균 매출 (억)'),
        'evidence': [
            ('TOP5 변화', "1,256억 ('22) → 1,240억 ('26.1Q) · -1% 거의 정체"),
            ('기타 KR 변화', "1,308억 → 724억 · -45% 거의 반토막"),
            ('해외 퍼블 변화', "1,271억 → 2,107억 · +66% 급증"),
            ('구조적 해석', '시장 규모는 커졌지만 <strong>중소 KR 퍼블이 줄어든 자리를 해외 퍼블이 차지</strong>하는 구도'),
            ('요점', '"한국이 죽었다"가 아니라 "<strong>중소 KR 퍼블이 해외 퍼블에게 밀렸다</strong>"가 정확. TOP5는 상대적으로 버티는 중'),
        ],
    },
    {
        'id': 'kr-3',
        'section': 'KR',
        'headline': '카카오가 토해낸 200억+을 중화권 Survival이 가져갔다',
        'interpretation': 'MMORPG가 지는 자리를 중화권의 Survival/Strategy (Last War·Whiteout·Kingshot)가 채우는 <strong>장르 대전환</strong>. 같은 금액이 이동하는 게 아니라 <strong>장르 자체가 교체</strong>되는 중.',
        'chart': before_after_bars([
            ('KR MMORPG', 1818, 1382, '#dc2626'),
            ('KR Strategy', 515, 1151, '#059669'),
        ], title='KR 장르별 매출 — MMORPG vs Strategy 교체 (억/월)'),
        'evidence': [
            ('요점', 'MMORPG 비운 자리(-436)를 Strategy(+636)가 덮어쓰는 구도'),
        ],
    },
    {
        'id': 'kr-4',
        'section': 'KR',
        'headline': '한국 점유율은 이미 20%p 빼앗겼다 (67% → 48%)',
        'interpretation': '매출만 보면 -6% 감소이지만, 점유율로 보면 <strong>20%p 가까이 빠짐</strong>. 지금 추세면 26~27년 사이 <strong>중화권이 KR 퍼블 점유율을 추월</strong>할 가능성 있음.',
        'chart': line_chart([
            {'name':'KR 퍼블', 'color':'#3b82f6', 'values':[66.9, 63.7, 50.7, 50.1, 48.2]},
            {'name':'중화권', 'color':'#f59e0b', 'values':[21.8, 25.5, 35.8, 36.9, 37.7]},
        ], ['22', '23', '24', '25', '26.1Q'], title='KR 시장 점유율 추이 (%)', y_max=80, unit='%'),
        'evidence': [
            ('요점', '격차 45%p → 10.5%p로 급축소 (34.5%p 좁혀짐)'),
        ],
    },
    {
        'id': 'kr-5',
        'section': 'KR',
        'headline': '유저는 줄어들어도 돈은 더 쓴다 — "고래 유저화"',
        'interpretation': 'MAU 10% 감소에도 매출 13% 성장. 그 이유는 <strong>ARPMAU 25% 증가</strong>. 신규 유입보다 <strong>기존 고래 유저 LTV 극대화</strong>가 더 중요한 시장.',
        'chart': '',
        'evidence': [
            ('MAU 변화', '4,291만 → 3,615만 (-16%)'),
            ('ARPMAU 변화', '8,938원 → 13,263원 (+48%)'),
            ('요점', '"적은 유저 + 더 높은 단가" = 고래 시장 구조'),
        ],
    },
    {
        'id': 'kr-6',
        'section': 'KR',
        'headline': '신규 진입 게임도 줄었다 — 월 8.5개 → 6.9개 (-18%)',
        'interpretation': '유저가 줄고 단가가 오르면 <strong>신작 공급도 줄어든다</strong>. KR TOP 100에 진입하는 월평균 신작이 <strong>8.5개(22) → 6.9개(25)로 18% 감소</strong>.<br><br>퍼블 국적별로 보면 더 흥미롭다 — <strong>KR·중화권 모두 투입 감소</strong> 중이지만 <strong>중화권은 장르 다변화(RPG 줄이고 Strategy·Casual 늘림)</strong>로 대응. KR 퍼블은 모든 장르가 다 줄었음.',
        'chart': line_chart_multi([
            {'name':'KR', 'color':'#3b82f6', 'values':[3.2, 3.2, 3.4, 2.5]},
            {'name':'중화권', 'color':'#f59e0b', 'values':[3.5, 4.2, 4.1, 3.0]},
            {'name':'기타', 'color':'#64748b', 'values':[0.5, 0.7, 0.5, 1.2]},
        ], ['2022','2023','2024','2025'], title='KR 월평균 신규 진입 수 — 퍼블 국적별 (개/월)', y_max=5, y_step=1, unit='개'),
        'evidence': [
            ('전체 월평균 진입', "'22 8.5개 → '25 6.9개 (-18%)"),
            ('KR 퍼블', '3.2 → 2.5 (-22%) · 모든 장르 물량 감소'),
            ('중화권', '3.9 → 3.0 (-23%) · RPG 줄이고 비RPG 증가'),
            ('기타', '0.6 → 1.2 (+100%) · 비중은 작지만 증가세'),
            ('요점', '"시장이 포화 상태" — <strong>더 많은 신작보다 더 나은 신작</strong>이 필요한 시장'),
        ],
    },
    {
        'id': 'kr-7',
        'section': 'KR',
        'headline': '중화권 RPG 생존율이 반토막 났다 (57% → 30%)',
        'interpretation': '전체 3개월 생존율은 44% → 48%로 거의 안정이지만, 숨은 큰 변화가 있다. <strong>중화권 RPG 생존율이 57%→30%로 꾸준히 하락</strong>. 같은 중화권이라도 <strong>Strategy·Casual (비RPG)는 60%+로 양호</strong>.<br><br>이게 의미하는 건 <strong>"중화권 RPG 대량 투입 전략이 더 이상 안 먹힌다"</strong>는 것. KR 유저가 더 이상 중화권 양산형 RPG에 반응하지 않음. 그래서 중화권도 Strategy(Last War 류) · Casual(Puzzle 류)로 투입 방향을 바꾸는 중.',
        'chart': line_chart_multi([
            {'name':'중화권 RPG', 'color':'#dc2626', 'values':[57.1, 48.3, 45.8, 30.0]},
            {'name':'중화권 비RPG (Strategy·Casual)', 'color':'#10b981', 'values':[50.0, 53.8, 62.5, 62.5]},
            {'name':'KR 퍼블 (참고)', 'color':'#3b82f6', 'values':[35.7, 50.0, 50.0, 48.1]},
        ], ['2022','2023','2024','2025'], title='KR TOP100 신규 진입 3개월 생존율 — 그룹별 (%)', y_max=80, y_step=20, unit='%'),
        'evidence': [
            ('중화권 RPG', "'22 57% → '25 30% (-27%p) · 꾸준한 하락"),
            ('중화권 비RPG', "'22 50% → '25 62.5% (+12.5%p) · 안정 양호"),
            ('KR 퍼블 전체', "'22 44% → '25 48% (+4%p) · 유지"),
            ('NHN 사례', "우파루 오딧세이(23년 Simulation 진입) 생존 성공 — 비웹보드 신작도 가능성 검증"),
            ('요점', '<strong>"중화권 RPG 양산 모델 종료"</strong> — 장르 차별화가 생존의 핵심 조건'),
        ],
    },

    # JP
    {
        'id': 'jp-1',
        'section': 'JP',
        'headline': '일본은 정체 — 자국 IP 노후화로 -4%',
        'interpretation': '표면 -4% 감소이지만 속은 <strong>JP 자국 퍼블 -13% (-748억/월) 급락</strong>. 15년 넘은 대표 IP들이 일제히 쇠락하는 <strong>세대 교체 실패</strong>.',
        'chart': bar_compare([
            ('모스터스트라이크', -259, '#dc2626', 'XFLAG'),
            ('우마무스메', -238, '#dc2626', 'Cygames'),
            ('Pokémon TCG Pocket', -192, '#dc2626', 'Pokémon'),
            ('Fate/Grand Order', -101, '#dc2626', 'Aniplex'),
            ('프로야구 스피리츠A', -98, '#dc2626', 'KONAMI'),
        ], title='JP 자국 퍼블 IP 쇠락 TOP 5 (억/월 감소)'),
        'evidence': [
            ('요점', 'JP 자국 퍼블 -748억 = KR 카카오게임즈 -214억의 3.5배 충격'),
        ],
    },
    {
        'id': 'jp-2',
        'section': 'JP',
        'headline': '일본도 중화권이 가져갔다 — 다만 속도 완만',
        'interpretation': '중화권 +13% 성장으로 JP 자국 하락(-748억)의 <strong>절반 상쇄</strong>. KR(49%)보다는 느리지만 JP도 <strong>중화권 침투 진행 중</strong>. 일본 시장의 폐쇄성 때문에 속도가 상대적으로 느릴 뿐.',
        'chart': '',
        'evidence': [
            ('중화권 매출', '2,669 → 3,027억 (+358억, +13%)'),
            ('JP 점유율', "'22 62.9% → '26.1Q 51.4% (-11.5%p)"),
            ('중화권 점유율', "'22 25.9% → '26.1Q 34.8% (+8.9%p)"),
            ('요점', 'KR 퍼블은 3.1% → 0.9%로 <strong>거의 퇴출</strong> — NHN 진입 허들 상승'),
        ],
    },
    {
        'id': 'jp-3',
        'section': 'JP',
        'headline': 'JP 1위 타이틀 규모가 37% 줄었다 — 메가히트 부재',
        'interpretation': '1위 게임이 <strong>748억 (22) → 470억 (25)</strong>로 축소. 중위권은 제자리 상태인 걸 보면 <strong>새로운 메가히트가 안 나오고 기존 IP만 천천히 죽어가는</strong> 구조. 시장 에너지 감소 신호.<br><br>로그 스케일 차트로 보면 1위 라인이 유일하게 꺾이는 반면, 10~100위는 평행 유지 → <strong>상위권 붕괴가 전체 시장 축소를 단독 주도</strong>.',
        'chart': rank_line_chart(
            {
                '1위':   [748, 640, 559, 470, 433],
                '10위':  [213, 190, 235, 219, 223],
                '20위':  [105, 111, 139, 127, 131],
                '50위':  [62, 47, 58, 52, 54],
                '100위': [40, 26, 29, 59, 35],
            },
            ['2022', '2023', '2024', '2025', '26.1Q'],
            country_color='#ef4444',
            title='JP 순위별 매출 추이 (로그 스케일, 억/월)',
        ) + mini_table(
            ['순위', '22년', '23년', '24년', '25년', '26.1Q'],
            [
                ('1위', '748', '640', '559', '470', '433'),
                ('10위', '213', '190', '235', '219', '223'),
                ('20위', '105', '111', '139', '127', '131'),
                ('50위', '62', '47', '58', '52', '54'),
                ('100위', '40', '26', '29', '59', '35'),
            ]
        ),
        'evidence': [
            ('1위 변화', '748 → 433억 (-42%) · 유일하게 큰 폭 하락'),
            ('10위 변화', '213 → 223억 (+5%) · 제자리'),
            ('50위 변화', '62 → 54억 (-13%) · 소폭 하락'),
            ('100위 변화', '40 → 35억 (-13%) · 소폭 하락'),
            ('요점', '<strong>상위권만 붕괴, 중위권은 제자리</strong> → 시장 에너지 감소 신호 · 메가히트 부재'),
        ],
    },

    # US
    {
        'id': 'us-1',
        'section': 'US',
        'headline': '미국은 진짜 시장이다 — +17% 성장, 월 +2,935억',
        'interpretation': 'KR·JP가 정체/축소 중일 때 US는 <strong>+2,935억/월 순증가</strong>. 매출 규모 자체가 KR의 4배 이상. <strong>"성장 시장에서 경쟁할 것이냐, 축소 시장에서 방어할 것이냐"</strong>의 전략 선택.',
        'chart': before_after_bars([
            ('KR 시장', 4109, 4654, '#3b82f6'),
            ('JP 시장', 9306, 8969, '#ef4444'),
            ('US 시장', 16801, 19736, '#a855f7'),
        ], title='3국 시장 규모 — 25년 전후 (억/월)'),
        'evidence': [
            ('US 100위 규모', '43~86억/월 ≈ <strong>KR 20위 수준</strong>'),
            ('요점', 'US 중위권 = KR 상위권. 진입만 하면 3~4배 매출 잠재력'),
        ],
    },
    {
        'id': 'us-2',
        'section': 'US',
        'headline': 'Last War가 US 성장의 단독 드라이버 (+316억)',
        'interpretation': 'US 성장분 +2,935억 중 중화권이 <strong>+2,065억 (70% 기여)</strong>. 그 중 <strong>Last War:Survival</strong> 혼자 409→725억 (+316억). <strong>KR·US 공통 메가히트</strong>.',
        'chart': before_after_bars([
            ('Last War (FUNFLY)', 409, 725, '#f59e0b'),
            ('Royal Match (Dream)', 624, 904, '#10b981'),
            ('MONOPOLY GO!', 1384, 1061, '#dc2626'),
        ], title='US 대표 게임 — 25년 전후 매출 변화 (억/월)'),
        'evidence': [
            ('요점', '중화권 1개 게임이 시장 단독 +316억 견인'),
        ],
    },
    # us-3 (미국 진입/생존율) 제외 — 신규 진입 분석 수정 완료 후 추가 예정

    # COMMON
    {
        'id': 'common-1',
        'section': 'COMMON',
        'headline': '중화권이 3국 모두에서 점유율 뺏어가는 중',
        'interpretation': '<strong>국가 불문 공통 트렌드</strong>. KR +16%p, JP +9%p, US +11%p. 중화권 퍼블리셔가 <strong>글로벌 전체에서 동시 다발적 확장</strong> — 한국만의 이슈가 아닌 업계 구조적 변화.',
        'chart': line_chart([
            {'name':'KR', 'color':'#3b82f6', 'values':[21.8, 25.5, 35.8, 36.9, 37.7]},
            {'name':'JP', 'color':'#ef4444', 'values':[25.9, 26.7, 31.8, 32.5, 34.8]},
            {'name':'US', 'color':'#a855f7', 'values':[15.5, 13.8, 15.4, 22.3, 26.8]},
        ], ['22', '23', '24', '25', '26.1Q'], title='3국 중화권 점유율 추이 (%)', y_max=50, unit='%'),
        'evidence': [
            ('3국 중화권 합계 증가', '+3,003억/월 (+46%)'),
            ('요점', '중화권 1개 퍼블리셔(FUNFLY 등)가 3국 시장 동시 흔드는 구도'),
        ],
    },
    {
        'id': 'common-2',
        'section': 'COMMON',
        'headline': 'MAU 감소·ARPMAU 상승은 3국 공통 뉴노멀',
        'interpretation': '유저는 줄어도 매출은 증가 — 이게 <strong>글로벌 모바일 게임 시장의 뉴노멀</strong>. 신규 유입 의존 시대는 끝. <strong>기존 유저 LTV 극대화 + 고가 상품(50만원+ 패키지)</strong> 구축이 핵심.',
        'chart': '',
        'evidence': [
            ('3국 MAU', '4,014만 → 3,615만 (-10%)'),
            ('3국 ARPMAU', '10,328 → 12,873원 (+25%)'),
            ('3국 DL', '582 → 539만건 (-7%)'),
            ('요점', '신규 유입 ↓ but 단가 ↑ → <strong>고래 유저화</strong> 시대'),
        ],
    },

    # WEBBOARD
    {
        'id': 'wb-1',
        'section': 'WEBBOARD',
        'headline': '웹보드 시장은 일반 시장의 1.6배 속도로 크고 있다',
        'interpretation': '일반 게임 시장 +13%일 때 웹보드 <strong>+22% 성장</strong>. 규제 시장임에도 성장성 유지. 이유는 <strong>ARPMAU가 일반 시장 대비 16% 높음</strong> — 소수 고과금 유저의 결제 밀도가 매우 높음.',
        'chart': before_after_bars([
            ('KR 일반 시장', 4109, 4654, '#3b82f6'),
            ('KR 웹보드', 137, 168, '#0085ca'),
        ], title='KR 일반 vs 웹보드 시장 성장 (억/월)'),
        'evidence': [
            ('웹보드 ARPMAU', '15,429원 (일반 13,263원의 1.16배)'),
            ('요점', '규제 시장 + 고래 유저 + 중독성 → 매출 효율 일반 시장 추월'),
        ],
    },
    {
        'id': 'wb-2',
        'section': 'WEBBOARD',
        'headline': 'NHN은 웹보드에서 절대 강자 (74% 점유)',
        'interpretation': 'KR 메인 시장이 양극화되는 와중에 NHN은 <strong>웹보드 내 점유율 74%로 독점</strong>. 네오위즈 15%대의 <strong>4~5배 격차</strong>. 이 도메인 자체가 NHN의 프리미엄 영역.',
        'chart': line_chart([
            {'name':'NHN', 'color':'#0085ca', 'values':[62.7, 73.7, 76.4, 79.1, 68.7]},
            {'name':'네오위즈', 'color':'#ff6b35', 'values':[23.5, 20.8, 19.1, 17.3, 15.4]},
            {'name':'Zempot WPL', 'color':'#8b5cf6', 'values':[0.4, 0.0, 0.0, 3.0, 9.4]},
        ], ['22', '23', '24', '25', '26.1Q'], title='웹보드 퍼블리셔별 점유율 (%)', y_max=90, unit='%'),
        'evidence': [
            ('요점', 'NHN 점유율 4배 격차 유지 · WPL 26.1Q 급부상'),
        ],
    },
    {
        'id': 'wb-3',
        'section': 'WEBBOARD',
        'headline': 'NHN 3종은 4년간 단 1개월도 안 빠졌다',
        'interpretation': '한게임 포커·섯다&맞고·포커클래식 <strong>3종 모두 TOP 100 51개월 전 기간 연속 체류</strong>. 일반 게임 12개월 생존율(40%)과 비교하면 웹보드는 완전히 다른 카테고리.',
        'chart': '',
        'evidence': [
            ('한게임 포커', '40 → 43억 (+8%) · 51개월 무중단'),
            ('한게임 섯다&맞고', '27 → 39억 (+44%) · 51개월 무중단'),
            ('한게임포커 클래식', '27 → 34억 (+26%) · 51개월 무중단'),
            ('한게임 신맞고', '9 → 10억 (+3%) · 51개월 무중단'),
            ('요점', '3종 모두 <strong>무중단 + 성장</strong> = 포트폴리오의 강인함'),
        ],
    },
    {
        'id': 'wb-4',
        'section': 'WEBBOARD',
        'headline': 'WPL(Zempot)이 5배 급성장 — 신흥 위협 1순위',
        'interpretation': '25년 8월까지 3억대였던 WPL이 <strong>25년 9월 13억으로 급등, 현재 19억대</strong>. 원인은 <strong>오프라인 대회(WPH, 상금 10억) + 50만원 고단가 패키지 + 임요환 등 프로 선수 활용 스포츠 브랜딩</strong>. "이스포츠 플랫폼"으로 전환.',
        'chart': line_chart([
            {'name':'WPL', 'color':'#8b5cf6', 'values':[3.2, 3.7, 13.4, 16.2, 19.0]},
        ], ['25.7', '25.8', '25.9', '25.11', '26.3'], title='WPL 월별 매출 급증 (억/월)', y_max=25, unit='억'),
        'evidence': [
            ('급성장 원인', '① 오프라인 대회(WPH) 상금 10억 · ② 50만원+ 고단가 패키지 · ③ 임요환 라이브 콘텐츠 · ④ 리그 상설화'),
            ('요점', '"실력 기반 스포츠" 프레임 — 국내 웹보드 규제(5만원 한도) 우회 + 프리미엄 타겟'),
        ],
    },
    {
        'id': 'wb-5',
        'section': 'WEBBOARD',
        'headline': '네오위즈는 30억대에서 4년째 멈춰 있다',
        'interpretation': '피망 포커·뉴맞고 합계 <strong>30억대 정체 (2022~2026)</strong>. 광고 유입률이 NHN 대비 1/4~1/5 수준 — <strong>마케팅 투자 부재로 브랜드 영향력 약화</strong>. 이 틈을 WPL이 파고드는 중.',
        'chart': before_after_bars([
            ('NHN 포커 광고율', 24.7, 32.1, '#0085ca'),
            ('Pmang Poker 광고율', 11.3, 20.6, '#ff6b35'),
            ('NHN 신맞고 광고율', 42.0, 45.1, '#0085ca'),
            ('피망 뉴맞고 광고율', 8.1, 9.3, '#ff6b35'),
        ], title='광고 유입률 비교 (%) — NHN vs 네오위즈', unit='%'),
        'evidence': [
            ('요점', 'NHN 광고율 2~5배 높음 → 마케팅 공세의 차이'),
        ],
    },

    # STRATEGY
    {
        'id': 'strategy-1',
        'section': 'STRATEGY',
        'headline': 'NHN의 진짜 강점은 "도메인 독점"',
        'interpretation': 'KR 일반 시장에서는 점유율 방어도 어려운 상황. 반면 NHN은 <strong>웹보드라는 특수 도메인에서 74% 독점</strong>. 규제 시장이라 중화권도 진입 어려움. <strong>웹보드는 NHN의 해자(moat)</strong>.',
        'chart': bar_compare([
            ('NHN 일반 시장 점유율', 3, '#64748b', 'TOP5 중 5위'),
            ('NHN 웹보드 점유율', 74, '#0085ca', '독점적 지위'),
        ], title='NHN 점유율 — 일반 vs 웹보드', unit='%', max_val=100),
        'evidence': [
            ('수명 비교', '일반 12개월 생존율 40% vs <strong>웹보드 NHN 3종 100%</strong>'),
            ('요점', '"일반 게임 확장"보다 "웹보드 강화 + 글로벌 확장"이 효율적'),
        ],
    },
    {
        'id': 'strategy-2',
        'section': 'STRATEGY',
        'headline': 'US 진출하면 KR 상위권 매출이 100위권에서 나온다',
        'interpretation': 'US 시장 100위 게임이 <strong>43~86억/월</strong> — KR 20위권 수준. NHN 웹보드가 US 진출하면 <strong>중위권만 안착해도 현재 KR 매출의 2~3배</strong> 잠재력.',
        'chart': mini_table(
            ['순위', 'KR', 'JP', 'US'],
            [
                ('1위', '510억', '559억', '2,267억'),
                ('10위', '85억', '235억', '329억'),
                ('20위', '48억', '139억', '212억'),
                ('50위', '21억', '58억', '105억'),
                ('100위', '9억', '29억', '62억'),
            ]
        ),
        'evidence': [
            ('요점', 'US 100위 ≈ KR 20위 → 진입만 하면 <strong>3~4배 매출</strong> 가능성'),
        ],
    },

    # ============ 신규 게임 출시 방향성 (3개) ============
    {
        'id': 'launch-1',
        'section': 'STRATEGY',
        'headline': '[신작 장르] Strategy는 이미 레드오션 — Puzzle/Casual이 실질 기회',
        'interpretation': '가장 성장하는 장르는 Strategy지만 이미 <strong>중화권이 장악 (FUNFLY Last War, Kingshot 등)</strong>. 후발주자 NHN이 들어가 봤자 자본·IP·오퍼레이션 모두 밀림. 반면 <strong>Puzzle은 터키(Dream Games)·핀란드(Supercell) 등 분산 구조</strong>이고, Casual은 글로벌 퍼블 혼재라 <strong>빈틈 있음</strong>.',
        'chart': bar_compare([
            ('KR Strategy', 636, '#dc2626', '+123% 중화권 장악'),
            ('KR Puzzle', 194, '#059669', '+97% 분산 구조'),
            ('KR 비MMORPG RPG', 168, '#059669', '+24% 가능성'),
            ('KR Casual', 25, '#059669', '+32% 틈새'),
        ], title='KR 장르별 25년 전후 매출 증가액 (억/월)'),
        'evidence': [
            ('Strategy 중화권 비중', 'KR Strategy 성장의 90%+ = 중화권 게임'),
            ('Puzzle 리더', 'Dream Games(터키), Supercell(핀란드) — 분산'),
            ('요점', '<strong>레드오션 피하고 분산된 장르(Puzzle/Casual) 노리기</strong>가 전략적'),
        ],
    },
    {
        'id': 'launch-2',
        'section': 'STRATEGY',
        'headline': '[타겟 국가] US 직진보단 "JP 자국 IP 인수 → 글로벌" 우회 경로',
        'interpretation': 'US 직진은 자본·마케팅 비용 폭증 + 경쟁 빡셈. 대안: <strong>JP 자국 IP가 쇠락 중 (모스터스트라이크 -259억, 우마무스메 -238억 등 대형 IP 매출 반토막)</strong>. 저평가된 IP 인수 or 글로벌 운영 라이선스 획득 후 <strong>NHN 운영 노하우로 재활성화</strong>하는 경로. 중화권이 아닌 NHN만의 차별화 접근.',
        'chart': bar_compare([
            ('모스터스트라이크', -259, '#dc2626', 'XFLAG · 40% 감소'),
            ('우마무스메', -238, '#dc2626', 'Cygames · 45% 감소'),
            ('Pokémon TCG Pocket', -192, '#dc2626', 'Pokémon · 38% 감소'),
            ('Fate/Grand Order', -101, '#dc2626', 'Aniplex · 21% 감소'),
        ], title='쇠락 중인 JP 자국 IP — 글로벌 재활 기회 (억/월 감소)'),
        'evidence': [
            ('JP 자국 퍼블 점유율', '62.9% → 51.4% (-11.5%p)'),
            ('쇠락 IP 특성', '팬덤/IP 자산 있음 + 운영 노후화 + 글로벌 확장 부진'),
            ('NHN 차별화', '<strong>웹보드 운영 노하우 (리텐션·결제 최적화)</strong>를 IP 게임에 이식'),
            ('요점', '"US 정면 돌파" 대신 "<strong>JP 저평가 IP 인수 + 글로벌 재출시</strong>"가 자본 효율적'),
        ],
    },
    {
        'id': 'launch-3',
        'section': 'STRATEGY',
        'headline': '[퍼블 협업] 중화권 Publishing 파트너 대신 "스포츠/리그 플랫폼 IP"',
        'interpretation': '중화권과의 Publishing 제휴는 <strong>매출 지분 분배 + 중화권 의존 심화</strong> 리스크. 대안: <strong>WPL 사례에서 증명된 "스포츠/리그 프레임"</strong>. 한국 웹보드 규제(5만원 한도) 회피 + 프리미엄 고과금 유저 타겟. NHN 웹보드 자산 + 스포츠 이벤트 IP 결합이 유망.',
        'chart': '',
        'evidence': [
            ('WPL 성장 사례', '25.9월 3.7 → 19억 (5배) — 오프라인 대회 + 고단가 BM 전략'),
            ('스포츠 브랜딩 효과', '임요환 등 프로 선수 활용 → 고과금 유저 확보'),
            ('규제 회피', '"실력 기반 스포츠" 프레임 = 5만원 결제 한도 우회 가능'),
            ('NHN 적용 가능', '포커 토너먼트 + 섯다&맞고 리그 + e스포츠 공동 주최 등'),
            ('요점', 'WPL이 뚫은 길 = NHN도 따라갈 수 있는 로드맵. <strong>웹보드 자산 + 스포츠 IP 결합</strong>'),
        ],
    },
    {
        'id': 'launch-4',
        'section': 'STRATEGY',
        'headline': '[종합 우선순위] NHN 신규 출시 3대 방향 — 장르 × 시장 × 방식',
        'interpretation': '위 3개 분석 종합: <strong>①장르 Puzzle/Casual ②시장 JP 자국 IP 인수 + US 추후 진출 ③방식 스포츠/리그 플랫폼 확장</strong>. 리스크 vs 수익 균형 고려한 순서.',
        'chart': mini_table(
            ['우선순위', '방향', '근거', '리스크'],
            [
                ('1순위', '웹보드 리그 플랫폼 확장 (WPL 벤치마크)', '검증된 BM + 규제 우회', '낮음'),
                ('2순위', 'JP 자국 IP 인수 → 글로벌 재출시', 'IP 저평가 + NHN 운영력', '중간 (M&A 실행)'),
                ('3순위', 'Puzzle/Casual 신작 US 진출', '시장 규모 ↑ 경쟁 분산', '높음 (자본 투입)'),
            ]
        ),
        'evidence': [
            ('회피할 선택', '<strong>Strategy 장르 신작</strong> (중화권 레드오션), <strong>중화권 퍼블 Publishing 제휴</strong> (의존 심화)'),
            ('요점', '검증된 도메인(웹보드) 확장 → IP 인수 → 신장르 신작 순으로 <strong>리스크 계단</strong> 구축'),
        ],
    },
]

SECTION_META = {
    'KR':       ('🇰🇷 한국 시장',    '#3b82f6', '#dbeafe'),
    'JP':       ('🇯🇵 일본 시장',    '#ef4444', '#fee2e2'),
    'US':       ('🇺🇸 미국 시장',    '#a855f7', '#f3e8ff'),
    'COMMON':   ('🌏 3국 공통 트렌드', '#64748b', '#f1f5f9'),
    'WEBBOARD': ('🎴 웹보드 심층',   '#0085ca', '#e0f2fe'),
    'STRATEGY': ('🎯 전략 시사점',   '#d97706', '#fef3c7'),
}

BRIDGES = {
    'kr-1': '그럼 KR 퍼블 내부는 구체적으로 어떻게 변했나?',
    'kr-2': '근데 TOP5만 볼 게 아니다 — 더 큰 구조 변화가 "그 외" 영역에서 일어났다',
    'kr-2b': '카카오가 토해낸 200억+이 어디로 갔는지 보자',
    'kr-3': '이 장르 이동이 시장 구조 전체에는 얼마나 큰 충격인가?',
    'kr-4': '점유율은 빼앗기는데 전체 매출은 증가 — 그 비결은?',
    'kr-5': '그럼 유저·매출 변화에 맞춰 신작 공급도 줄어들고 있을까?',
    'kr-6': '물량이 줄면 성적(생존율)은 어떻게 됐나? 여기서 진짜 놀라운 발견',
    'jp-1': '그럼 자국 퍼블이 빠진 자리를 누가 메우고 있나?',
    'jp-2': '시장 에너지 자체는 어떻게 변했나? (메가히트 관점)',
    'us-1': '그 +17% 성장을 누가 단독으로 견인했나?',
    # 'us-2' 브릿지 제거 — us-3 삭제로 US 섹션 마지막 인사이트가 us-2가 됨
    'common-1': '그럼 이 글로벌 재편 속 유저 행동은 어떻게 변했나?',
    'wb-1': '이 고성장 웹보드 시장에서 NHN의 위치는?',
    'wb-2': '그 74% 점유율의 기반은 무엇인가?',
    'wb-3': '그런데 최근 NHN 방패에 균열을 만드는 신흥 위협이 등장했다',
    'wb-4': '기존 경쟁자 네오위즈는 왜 이 틈을 못 막았나?',
    'strategy-1': '그 해자를 어디로 확장할 수 있나? 구체적으로는?',
    'strategy-2': '그럼 실제 신작 출시한다면 — 어느 장르로?',
    'launch-1': '장르 방향을 정했다면, 어느 시장으로 진출할까?',
    'launch-2': '시장과 IP 경로를 정했다면, 어떤 방식으로 펼칠까?',
    'launch-3': '지금까지 3가지 방향을 살펴봤다. 우선순위를 정리하면?',
}

def build_insight(ins, idx_in_section, total_in_section):
    color, bg = SECTION_META[ins['section']][1], SECTION_META[ins['section']][2]
    ev_html = ''
    for label, value in ins['evidence']:
        is_summary = label == '요점'
        cls = 'summary' if is_summary else ''
        icon = '💡 요점' if is_summary else label
        ev_html += f'<li class="evidence-item {cls}"><span class="ev-label">{icon}</span><span class="ev-value">{value}</span></li>'

    chart = ins.get('chart', '')
    chart_html = f'<div class="chart-wrap">{chart}</div>' if chart else ''

    # 순번 배지
    num_badge = f'<span class="insight-num" style="background:{color};">{idx_in_section}</span>'

    # 미리보기: interpretation 첫 문장 추출
    import re as _re
    first_sentence = _re.sub(r'<[^>]+>', '', ins['interpretation'].split('.')[0]).strip()[:100]

    # 큰 순번 배지 (카드 좌측)
    big_num = f'<div class="insight-bignum" style="color:{color};">{idx_in_section:02d}</div>'

    insight_html = f'''<details class="insight" id="{ins['id']}" style="--accent:{color}; --bg:{bg};">
  <summary>
    <div class="summary-left">
      {big_num}
    </div>
    <div class="summary-main">
      <div class="headline">{ins['headline']}</div>
      <div class="preview">{first_sentence}...</div>
    </div>
    <div class="expand-hint">근거 보기 ▸</div>
  </summary>
  <div class="body">
    <div class="interpretation">{ins['interpretation']}</div>
    {chart_html}
    <ul class="evidence-list">{ev_html}</ul>
  </div>
</details>'''

    # 브릿지 (다음 인사이트로 이어주는 문구) — 더 subtle한 연결선
    bridge_text = BRIDGES.get(ins['id'])
    if bridge_text and idx_in_section < total_in_section:
        insight_html += f'<div class="bridge" style="--bc:{color};"><div class="bridge-line"></div><span class="bridge-text">{bridge_text}</span><div class="bridge-line"></div></div>'

    return insight_html

SECTION_INTRO = {
    'KR': '한국 시장은 축소된 것처럼 보이지만 실제로는 성장 중이다. 단, 성장의 주체가 바뀌었다. 그 이동의 흐름을 5단계로 짚는다.',
    'JP': '일본은 "정체 + 노후화" 이중고. 자국 IP가 빠진 자리를 누가 어떻게 메우는지 본다.',
    'US': '3국 중 유일한 성장 시장. 규모·생존율 모두 압도적이지만 최근 중화권 침투가 가속 중.',
    'COMMON': 'KR·JP·US가 각자 다른 움직임처럼 보이지만 공통 구조 변화가 있다.',
    'WEBBOARD': 'NHN의 진짜 강점이 드러나는 도메인. 성장성·지배력·충성도 모두 일반 시장 대비 우위.',
    'STRATEGY': '위 분석을 종합한 NHN의 방어·확장 전략 — 현재 자산과 신규 출시 방향성.',
}

sections_html = ''
for sec_key in ['KR','JP','US','COMMON','WEBBOARD','STRATEGY']:
    sec_name, color, bg = SECTION_META[sec_key]
    items = [i for i in INSIGHTS if i['section'] == sec_key]
    if not items: continue
    total = len(items)
    ih = ''.join(build_insight(ins, idx+1, total) for idx, ins in enumerate(items))
    intro = SECTION_INTRO.get(sec_key, '')
    sections_html += f'''
<div class="section" style="--sec-color:{color}; --sec-bg:{bg};">
  <div class="section-header">
    <div class="section-title">{sec_name}</div>
    <div class="section-count">{total}개 인사이트</div>
  </div>
  <div class="section-intro">{intro}</div>
  {ih}
</div>'''

tldr_cards = '''
<div class="tldr-grid">
  <div class="tldr-card" style="--c:#3b82f6;">
    <div class="tldr-label">KR 시장</div>
    <div class="tldr-value">+13%</div>
    <div class="tldr-sub">4,109억 → 4,654억<br>중화권이 단독 견인</div>
  </div>
  <div class="tldr-card" style="--c:#ef4444;">
    <div class="tldr-label">JP 시장</div>
    <div class="tldr-value">-4%</div>
    <div class="tldr-sub">9,306억 → 8,969억<br>자국 IP 노후화</div>
  </div>
  <div class="tldr-card" style="--c:#a855f7;">
    <div class="tldr-label">US 시장</div>
    <div class="tldr-value">+17%</div>
    <div class="tldr-sub">1.68조 → 1.97조<br>Last War 메가히트</div>
  </div>
  <div class="tldr-card" style="--c:#0085ca;">
    <div class="tldr-label">웹보드 시장</div>
    <div class="tldr-value">+22%</div>
    <div class="tldr-sub">137억 → 168억<br>NHN 점유율 74%</div>
  </div>
</div>'''

html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NHN 시장 분석 — 임원 보고용 핵심 인사이트</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Noto Sans KR',sans-serif; background:#f5f7fa; color:#1e293b; padding:40px 20px; line-height:1.6; }}
  .container {{ max-width:1000px; margin:0 auto; }}
  .header {{ background:linear-gradient(135deg,#1e293b,#0f172a); color:#fff; border-radius:14px; padding:32px 36px; margin-bottom:24px; box-shadow:0 4px 16px rgba(0,0,0,0.1); }}
  h1 {{ font-size:1.6rem; font-weight:800; margin-bottom:8px; letter-spacing:-0.5px; }}
  .header .subtitle {{ font-size:0.88rem; color:#cbd5e1; font-weight:400; line-height:1.6; }}
  .header .meta {{ margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.1); font-size:0.78rem; color:#94a3b8; }}
  .tldr-section {{ margin-bottom:28px; }}
  .tldr-label-main {{ font-size:0.82rem; font-weight:700; color:#475569; margin-bottom:12px; display:flex; align-items:center; gap:8px; }}
  .tldr-label-main::before {{ content:""; width:4px; height:16px; background:#0f172a; border-radius:2px; }}
  .tldr-grid {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; }}
  .tldr-card {{ background:#fff; border-radius:10px; padding:16px 18px; border-top:4px solid var(--c); box-shadow:0 2px 8px rgba(0,0,0,0.05); }}
  .tldr-label {{ font-size:0.72rem; color:#64748b; font-weight:600; }}
  .tldr-value {{ font-size:1.8rem; color:var(--c); font-weight:800; margin:4px 0; letter-spacing:-1px; }}
  .tldr-sub {{ font-size:0.68rem; color:#94a3b8; line-height:1.5; }}
  .section {{ margin-bottom:28px; }}
  .section-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; padding-bottom:8px; border-bottom:2px solid var(--sec-color); }}
  .section-title {{ font-size:1.15rem; font-weight:800; color:var(--sec-color); }}
  .section-count {{ font-size:0.78rem; color:#94a3b8; font-weight:600; background:var(--sec-bg); padding:3px 10px; border-radius:12px; }}
  .section-intro {{ font-size:0.86rem; color:#475569; line-height:1.6; padding:12px 16px; background:var(--sec-bg); border-radius:8px; margin-bottom:18px; border-left:3px solid var(--sec-color); }}
  /* 카드 갤러리 스타일 */
  .insight {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:0; overflow:hidden; transition:all 0.2s; box-shadow:0 1px 3px rgba(0,0,0,0.04); }}
  .insight:hover {{ box-shadow:0 4px 12px rgba(0,0,0,0.08); border-color:var(--accent); }}
  .insight[open] {{ box-shadow:0 6px 20px rgba(0,0,0,0.1); border-color:var(--accent); margin:8px 0; }}
  .insight summary {{ list-style:none; cursor:pointer; padding:20px 24px; display:grid; grid-template-columns:auto 1fr auto; align-items:center; gap:20px; background:#fff; transition:background 0.2s; }}
  .insight summary::-webkit-details-marker {{ display:none; }}
  .insight[open] summary {{ background:linear-gradient(to right, var(--bg) 0%, transparent 100%); border-bottom:1px solid #e2e8f0; }}

  /* 큰 순번 배지 */
  .summary-left {{ display:flex; align-items:center; justify-content:center; }}
  .insight-bignum {{ font-size:2.4rem; font-weight:900; line-height:1; letter-spacing:-2px; opacity:0.9; font-variant-numeric:tabular-nums; }}
  .summary-main {{ min-width:0; }}
  .insight .headline {{ font-size:1.02rem; font-weight:800; color:#0f172a; line-height:1.35; }}
  .insight .preview {{ font-size:0.78rem; color:#94a3b8; margin-top:6px; line-height:1.5; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:520px; }}
  .insight[open] .preview {{ display:none; }}
  .insight .expand-hint {{ font-size:0.78rem; color:var(--accent); font-weight:700; white-space:nowrap; padding:6px 12px; border:1.5px solid var(--accent); border-radius:20px; background:#fff; transition:all 0.2s; }}
  .insight summary:hover .expand-hint {{ background:var(--accent); color:#fff; }}
  .insight[open] .expand-hint {{ background:var(--accent); color:#fff; }}

  /* 브릿지 — 가로 연결선 스타일 */
  .bridge {{ display:flex; align-items:center; gap:12px; padding:14px 24px; margin:0; font-size:0.82rem; color:#94a3b8; font-style:italic; }}
  .bridge-line {{ flex:1; height:1px; background:linear-gradient(to right, transparent, var(--bc), transparent); opacity:0.5; }}
  .bridge-text {{ white-space:nowrap; padding:0 8px; }}
  .insight summary::-webkit-details-marker {{ display:none; }}
  .insight summary:hover {{ background:var(--bg); }}
  .insight[open] summary {{ background:var(--bg); border-bottom:1px solid #e2e8f0; }}
  .insight .headline {{ font-size:1rem; font-weight:700; color:#1e293b; flex:1; }}
  .insight .expand-hint {{ font-size:0.75rem; color:var(--accent); font-weight:600; white-space:nowrap; }}
  .insight[open] .expand-hint {{ opacity:0.6; }}
  .insight .body {{ padding:20px 22px; background:#fafbfc; }}
  .interpretation {{ font-size:0.92rem; color:#334155; line-height:1.75; padding:14px 18px; background:#fff; border-left:4px solid var(--accent); border-radius:0 6px 6px 0; margin-bottom:14px; }}
  .interpretation strong {{ color:var(--accent); font-weight:700; }}
  .chart-wrap {{ background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 18px; margin-bottom:14px; }}
  .evidence-list {{ list-style:none; display:flex; flex-direction:column; gap:6px; }}
  .evidence-item {{ display:grid; grid-template-columns:180px 1fr; gap:14px; font-size:0.82rem; padding:8px 12px; background:#fff; border-radius:6px; border:1px solid #f1f5f9; }}
  .evidence-item .ev-label {{ color:#64748b; font-weight:600; }}
  .evidence-item .ev-value {{ color:#1e293b; font-variant-numeric:tabular-nums; }}
  .evidence-item .ev-value strong {{ color:var(--accent); }}
  .evidence-item.summary {{ background:#fef3c7; border-color:#fbbf24; }}
  .evidence-item.summary .ev-label {{ color:#b45309; font-weight:700; }}
  .evidence-item.summary .ev-value {{ color:#78350f; font-weight:600; }}
  /* mini table */
  .mini-table {{ width:100%; border-collapse:collapse; font-size:0.82rem; margin:4px 0; }}
  .mini-table th {{ background:#f8fafc; padding:8px 10px; text-align:left; font-weight:700; color:#475569; border-bottom:2px solid #e2e8f0; font-size:0.78rem; }}
  .mini-table td {{ padding:7px 10px; border-bottom:1px solid #f1f5f9; }}
  .mini-table td.num {{ text-align:right; font-variant-numeric:tabular-nums; color:#1e293b; font-weight:600; }}
  .footer {{ text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:32px; padding:16px; border-top:1px solid #e2e8f0; }}
  @media (max-width:768px) {{
    .tldr-grid {{ grid-template-columns:1fr 1fr; }}
    .evidence-item {{ grid-template-columns:1fr; gap:4px; }}
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📊 NHN 시장 분석 — 핵심 인사이트 리포트</h1>
    <div class="subtitle">
      KR · JP · US 3국 시장 + 웹보드 심층 · 2022 ~ 2026.1Q 기간 분석<br>
      각 인사이트를 클릭하면 <strong>해석 + 차트 + 근거 데이터</strong>가 펼쳐집니다 (20개 핵심)
    </div>
    <div class="meta">
      기준: dw_app_monthly · in_revenue_top100_unified_os=TRUE · iOS+Android 합산 · revenue_krw_100 (ST 100% 보정 + 연도별 환율)<br>
      전/후 비교: 전(22~24, 36개월 월평균) vs 후(25~26.1Q, 15개월 월평균)
    </div>
  </div>

  <div class="tldr-section">
    <div class="tldr-label-main">한 줄 요약 (TL;DR)</div>
    {tldr_cards}
  </div>

  {sections_html}

  <div class="footer">
    출처: Sensor Tower · AI_mobilegame DB · 퍼블 국적 분류: NEXON→KR, FUNFLY→중화권 강제<br>
    총 {len(INSIGHTS)}개 핵심 인사이트 · 신규 진입 분석은 별도 업데이트 예정
  </div>
</div>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f: f.write(html)
print(f"[저장] {OUT}")
print(f"[크기] {os.path.getsize(OUT)/1024:.1f} KB")
