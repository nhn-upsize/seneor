#!/usr/bin/env python3
"""Move DART OP from separate column to inline under each year cell"""
import re

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

DART = {
    '엔씨소프트':    {2022:5590, 2023:1373, 2024:-1092, 2025:161},
    '넷마블':        {2022:-1087, 2023:-685, 2024:2156, 2025:3525},
    '카카오게임즈':  {2022:1758, 2023:745, 2024:191, 2025:-396},
    'NHN':           {2022:391, 2023:556, 2024:-326, 2025:1324},
    '컴투스':        {2022:-167, 2023:-332, 2024:61, 2025:26},
    '위메이드':      {2022:-849, 2023:-1104, 2024:71, 2025:107},
    '데브시스터즈':  {2022:-199, 2023:-480, 2024:272, 2025:64},
    '크래프톤':      {2022:7516, 2023:7680, 2024:11825, 2025:10544},
    '네오위즈':      {2022:196, 2023:316, 2024:329, 2025:600},
    '웹젠':          {2022:830, 2023:499, 2024:546, 2025:297},
    '펄어비스':      {2022:164, 2023:-164, 2024:-123, 2025:-148},
}

def fmt_op(v):
    if v >= 0:
        return f"<span style='color:#059669;font-size:0.58rem;'>OP {v:,}</span>"
    else:
        return f"<span style='color:#dc2626;font-size:0.58rem;'>OP {v:,}</span>"

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remove the DART header column
    old_header = '<th class="num" style="background:#e0e7ff;color:#3730a3;font-size:0.68rem;min-width:90px;">DART 영업이익<br>(억원, 연결)</th>'
    html = html.replace(old_header, '')
    print("Removed DART header column")

    # 2. Remove all DART data cells (added by previous script)
    # Pattern: <td class="num" style="background:#f0f0ff;...">...</td> right before </tr>
    # These are the cells with 22:/23:/24:/25: format
    dart_cell_pattern = r'<td class="num" style="background:#f0f0ff;font-size:0\.62rem;.*?</td>'
    count = len(re.findall(dart_cell_pattern, html))
    html = re.sub(dart_cell_pattern, '', html)
    print(f"Removed {count} DART inline cells")

    # Also remove empty DART cells from tot row
    html = html.replace('<td class="num" style="background:#f0f0ff;">-</td>', '')

    # Also remove simple dash cells
    dart_dash_pattern = r'<td class="num" style="background:#f8fafc;color:#cbd5e1;font-size:0\.68rem;">-</td>'
    count2 = len(re.findall(dart_dash_pattern, html))
    html = re.sub(dart_dash_pattern, '', html)
    print(f"Removed {count2} DART dash cells")

    # 3. Restore colspan from 8 back to 7
    # Only in the Step star section
    star_start = html.find('한국 퍼블리셔 월평균 매출')
    star_end = html.find('<div class="conclusion kr">')
    if star_start != -1 and star_end != -1:
        section = html[star_start:star_end]
        section = section.replace('colspan="8"', 'colspan="7"')
        html = html[:star_start] + section + html[star_end:]
        print("Restored colspan to 7")

    # 4. Add OP values inline under each year cell for DART publishers
    for pub_name, op_data in DART.items():
        # Find the publisher row
        search = f'<strong>{pub_name}</strong>'
        pos = html.find(search)
        if pos == -1:
            print(f"  SKIP: {pub_name} not found")
            continue

        # Find the <tr> that contains this publisher
        tr_start = html.rfind('<tr', 0, pos)
        tr_end = html.find('</tr>', pos) + 5

        if tr_start == -1 or tr_end == -1:
            continue

        row = html[tr_start:tr_end]

        # For each year cell, add OP value below the revenue number
        # The cells look like: <td class="num">979</td> or <td class="num dn">767</td>
        # or <td class="num col26 dn">314</td>
        # We need to match the 5 year cells (22,23,24,25,26.1Q)

        # Find all numeric td cells in this row (after the publisher name td)
        # Pattern: <td class="num...">NUMBER</td>
        cells = list(re.finditer(r'(<td class="num[^"]*">)(\d[\d,]*)(</td>)', row))

        if len(cells) < 5:
            print(f"  WARN: {pub_name} has {len(cells)} cells, expected >= 5")
            continue

        # The first 5 cells are years 22,23,24,25,26
        years = [2022, 2023, 2024, 2025]
        new_row = row

        # Process in reverse order to maintain positions
        for i in range(min(4, len(cells))):  # Only 22-25 (not 26.1Q, DART doesn't have 26)
            cell = cells[i]
            yr = years[i] if i < len(years) else None
            if yr and yr in op_data:
                op_val = op_data[yr]
                op_str = fmt_op(op_val)
                # Replace: >NUMBER</td> with >NUMBER<br>OP VALUE</td>
                old_cell = cell.group(0)
                new_cell = f'{cell.group(1)}{cell.group(2)}<br>{op_str}{cell.group(3)}'
                new_row = new_row.replace(old_cell, new_cell, 1)

        html = html[:tr_start] + new_row + html[tr_end:]
        print(f"  OK: {pub_name} - OP values added inline")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("\nDone! DART OP values now inline under each year cell.")

if __name__ == '__main__':
    main()
