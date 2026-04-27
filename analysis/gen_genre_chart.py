"""신규 진입 게임 장르 비중 — 2025 이전 vs 이후 (이미지 참고 스타일)"""
import sys, io
sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

rcParams["font.family"] = "Malgun Gothic"
rcParams["axes.unicode_minus"] = False
DPI = 200

OUT = "C:/Users/NHN/Documents/sensortower_api/output"

fig = plt.figure(figsize=(16, 7), facecolor="white")

# 상단 헤더
header = fig.add_axes([0, 0.88, 1, 0.12], facecolor="#1E2761")
header.set_xlim(0, 10); header.set_ylim(0, 10); header.axis("off")
header.text(5, 5, "신규 진입 게임 장르 비중 — 2025 이전 vs 이후", fontsize=22, fontweight="bold",
            color="white", ha="center", va="center")

# 좌우 구분
# 왼쪽: 2025 이전
left_header = fig.add_axes([0.02, 0.78, 0.47, 0.08], facecolor="#2C3E50")
left_header.set_xlim(0, 10); left_header.set_ylim(0, 10); left_header.axis("off")
left_header.text(5, 5, "2025 이전", fontsize=16, fontweight="bold", color="white", ha="center", va="center")

# 오른쪽: 2025 이후
right_header = fig.add_axes([0.51, 0.78, 0.47, 0.08], facecolor="#0D9488")
right_header.set_xlim(0, 10); right_header.set_ylim(0, 10); right_header.axis("off")
right_header.text(5, 5, "2025 이후", fontsize=16, fontweight="bold", color="white", ha="center", va="center")

# 데이터
data = {
    "KR 한국": {
        "pre": "RPG 51%, Strategy 12%, Action 9%, Casual 7%, Adventure 6%",
        "post": "RPG 44%, Strategy 15%, Simulation 10%, Casual 7%, Adventure 6%",
        "change": "Simulation 부상, RPG 비중 하락"
    },
    "JP 일본": {
        "pre": "RPG 41%, Action 11%, Simulation 10%, Adventure 9%, Strategy 8%",
        "post": "RPG 35%, Strategy 13%, Puzzle 13%, Adventure 10%, Simulation 9%",
        "change": "Strategy/Puzzle 약진, RPG 하락"
    },
    "US 미국": {
        "pre": "Strategy 17%, RPG 16%, Puzzle 16%, Casual 10%, Adventure 7%",
        "post": "Puzzle 20%, Simulation 13%, RPG 11%, Casual 10%, Strategy 10%",
        "change": "Puzzle 1위 등극, RPG 3위로 후퇴"
    },
}

country_colors = {"KR 한국": "#E74C3C", "JP 일본": "#2ECC71", "US 미국": "#3498DB"}

for i, (country, d) in enumerate(data.items()):
    y = 0.52 - i * 0.22
    color = country_colors[country]

    # 왼쪽 (이전)
    ax_left = fig.add_axes([0.02, y, 0.47, 0.18], facecolor="#F8FAFF")
    ax_left.set_xlim(0, 10); ax_left.set_ylim(0, 10); ax_left.axis("off")

    # 국가 배지
    ax_left.add_patch(mpatches.FancyBboxPatch((0.1, 3), 1.8, 4, boxstyle="round,pad=0.2",
                      facecolor=color, edgecolor="none", alpha=0.9))
    ax_left.text(1.0, 5, country[:2], fontsize=11, fontweight="bold", color="white", ha="center", va="center")

    # 장르 텍스트
    ax_left.text(2.3, 6.5, country[3:], fontsize=12, fontweight="bold", color="#1E2761")
    ax_left.text(2.3, 3.5, d["pre"], fontsize=10, color="#555")

    # 테두리
    ax_left.add_patch(mpatches.FancyBboxPatch((0, 0), 10, 10, boxstyle="round,pad=0.2",
                      facecolor="none", edgecolor="#DDD", lw=1))

    # 오른쪽 (이후)
    ax_right = fig.add_axes([0.51, y, 0.47, 0.18], facecolor="#F0FFFF")
    ax_right.set_xlim(0, 10); ax_right.set_ylim(0, 10); ax_right.axis("off")

    # 국가 배지
    ax_right.add_patch(mpatches.FancyBboxPatch((0.1, 3), 1.8, 4, boxstyle="round,pad=0.2",
                       facecolor=color, edgecolor="none", alpha=0.9))
    ax_right.text(1.0, 5, country[:2], fontsize=11, fontweight="bold", color="white", ha="center", va="center")

    # 장르 텍스트 + 변화 포인트
    ax_right.text(2.3, 7.0, country[3:], fontsize=12, fontweight="bold", color="#1E2761")
    ax_right.text(2.3, 4.0, d["post"], fontsize=10, color="#555")

    # 변화 포인트 배지
    ax_right.add_patch(mpatches.FancyBboxPatch((6.5, 0.5), 3.3, 2, boxstyle="round,pad=0.2",
                       facecolor="#0D9488", edgecolor="none", alpha=0.15))
    ax_right.text(8.15, 1.5, d["change"], fontsize=8.5, fontweight="bold", color="#0D9488",
                  ha="center", va="center")

    # 테두리
    ax_right.add_patch(mpatches.FancyBboxPatch((0, 0), 10, 10, boxstyle="round,pad=0.2",
                       facecolor="none", edgecolor="#DDD", lw=1))

# 하단 주석
fig.text(0.5, 0.02,
    "iOS + AOS 합산  |  매출 TOP 100 신규진입 기준  |  25년 이전 (22~24년) / 25년 이후 (25~26년)  |  Sensor Tower API",
    fontsize=9, ha="center", color="#AAA")

# 해석/인사이트
fig.text(0.02, 0.10, "해석: 전 시장에서 RPG 비중이 하락하고 있으며, 한국은 Simulation, 일본은 Strategy와 Puzzle, 미국은 Puzzle이 25년 이후 부상했다.",
         fontsize=9.5, color="#333", fontweight="bold")
fig.text(0.02, 0.06, "인사이트: RPG 일변도였던 한국과 일본 시장이 장르 다변화 추세로 전환, 미국은 이미 Puzzle/Casual 중심 시장으로 구조가 다르다.",
         fontsize=9.5, color="#1E2761", fontweight="bold")

buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", facecolor="white")
plt.close(fig)

with open(f"{OUT}/장르비중_25년전후비교.png", "wb") as f:
    f.write(buf.getvalue())
print("Done!")
