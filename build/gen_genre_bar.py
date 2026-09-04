"""신규 진입 게임 장르 비중 — 막대 그래프 (25년 이전 vs 이후)"""
import sys, io
sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

rcParams["font.family"] = "Malgun Gothic"
rcParams["axes.unicode_minus"] = False
DPI = 200

OUT = "C:/Users/NHN/Documents/sensortower_api/output"

# 데이터: 국가별 장르 비중 TOP 5
data = {
    "KR": {
        "pre":  {"RPG": 51, "Strategy": 12, "Action": 9, "Casual": 7, "Adventure": 6},
        "post": {"RPG": 44, "Strategy": 15, "Simulation": 10, "Casual": 7, "Adventure": 6},
    },
    "JP": {
        "pre":  {"RPG": 41, "Action": 11, "Simulation": 10, "Adventure": 9, "Strategy": 8},
        "post": {"RPG": 35, "Strategy": 13, "Puzzle": 13, "Adventure": 10, "Simulation": 9},
    },
    "US": {
        "pre":  {"Strategy": 17, "RPG": 16, "Puzzle": 16, "Casual": 10, "Adventure": 7},
        "post": {"Puzzle": 20, "Simulation": 13, "RPG": 11, "Casual": 10, "Strategy": 10},
    },
}

ctr_labels = {"KR": "KR 한국", "JP": "JP 일본", "US": "US 미국"}
ctr_colors = {"KR": "#E74C3C", "JP": "#2ECC71", "US": "#3498DB"}

# 전체 장르 목록 (등장 순서)
all_genres = []
for ctr in ["KR", "JP", "US"]:
    for pk in ["pre", "post"]:
        for g in data[ctr][pk]:
            if g not in all_genres:
                all_genres.append(g)

genre_colors = {
    "RPG": "#E74C3C", "Strategy": "#3498DB", "Action": "#F39C12", "Casual": "#9B59B6",
    "Adventure": "#1ABC9C", "Simulation": "#E67E22", "Puzzle": "#2ECC71", "Card": "#34495E",
}

fig, axes = plt.subplots(3, 2, figsize=(16, 10), gridspec_kw={"wspace": 0.25, "hspace": 0.45})
fig.patch.set_facecolor("white")

# 상단 제목
fig.text(0.5, 0.98, "신규 진입 게임 장르 비중 — 2025 이전 vs 이후",
         fontsize=20, fontweight="bold", ha="center", color="#1E2761")
fig.text(0.5, 0.955, "iOS + AOS 합산  |  매출 TOP 100 신규진입 기준  |  Sensor Tower API",
         fontsize=10, ha="center", color="#888")

for row, ctr in enumerate(["KR", "JP", "US"]):
    for col, (pk, pk_label) in enumerate([("pre", "25년 이전 (22~24)"), ("post", "25년 이후 (25~26)")]):
        ax = axes[row][col]
        ax.set_facecolor("#F8FAFF")

        d = data[ctr][pk]
        genres = list(d.keys())
        values = list(d.values())
        colors = [genre_colors.get(g, "#95A5A6") for g in genres]

        y_pos = np.arange(len(genres))
        bars = ax.barh(y_pos, values, color=colors, alpha=0.85, edgecolor="white", height=0.6)

        # 수치 표시
        for bar, v in zip(bars, values):
            ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
                    f"{v}%", va="center", fontsize=11, fontweight="bold", color="#333")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(genres, fontsize=11, fontweight="bold")
        ax.invert_yaxis()
        ax.set_xlim(0, 60)
        ax.set_xlabel("")
        ax.xaxis.set_visible(False)
        ax.spines[["top", "right", "bottom"]].set_visible(False)

        # 제목: 국가 + 기간 (같은 국가는 같은 색상)
        title_color = ctr_colors[ctr]
        ax.set_title(f"{ctr_labels[ctr]} — {pk_label}", fontsize=13, fontweight="bold",
                     color=title_color, pad=10)

# 하단 해석/인사이트
fig.text(0.03, 0.025,
    "해석: 전 시장에서 RPG 비중이 하락하고 있으며, 한국은 Simulation, 일본은 Strategy와 Puzzle, 미국은 Puzzle이 25년 이후 부상했다.",
    fontsize=9.5, color="#333")
fig.text(0.03, 0.005,
    "인사이트: RPG 일변도였던 한국과 일본 시장이 장르 다변화 추세로 전환, 미국은 이미 Puzzle과 Casual 중심 시장으로 구조가 다르다.",
    fontsize=9.5, color="#1E2761", fontweight="bold")

fig.tight_layout(rect=[0, 0.05, 1, 0.94])

buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", facecolor="white")
plt.close(fig)

with open(f"{OUT}/장르비중_막대그래프.png", "wb") as f:
    f.write(buf.getvalue())
print("Done!")
