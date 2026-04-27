"""대시보드 스타일 카드 — 신규 게임 3개월 생존율 국가별"""
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

data = {
    "KR": {"label": "KR 한국", "color": "#E74C3C",
           "ios_pre": 30.8, "ios_post": 24.0, "ios_n_pre": "11.6/mo", "ios_n_post": "11.8/mo",
           "aos_pre": 38.5, "aos_post": 22.0, "aos_n_pre": "11.1/mo", "aos_n_post": "12.2/mo"},
    "JP": {"label": "JP 일본", "color": "#2ECC71",
           "ios_pre": 37.9, "ios_post": 25.2, "ios_n_pre": "9.5/mo", "ios_n_post": "9.5/mo",
           "aos_pre": 29.0, "aos_post": 25.2, "aos_n_pre": "8.4/mo", "aos_n_post": "8.8/mo"},
    "US": {"label": "US 미국", "color": "#3498DB",
           "ios_pre": 36.1, "ios_post": 32.9, "ios_n_pre": "5.5/mo", "ios_n_post": "6.5/mo",
           "aos_pre": 38.6, "aos_post": 40.9, "aos_n_pre": "4.0/mo", "aos_n_post": "5.1/mo"},
}

fig = plt.figure(figsize=(14, 6.5), facecolor="white")

# 제목
fig.text(0.5, 0.96, "신규 게임 3개월 생존율 — 국가별 대시보드", fontsize=18, fontweight="bold",
         ha="center", color="#1E2761")
fig.text(0.5, 0.92, "매출 TOP 100 신규진입 기준  |  2025 전/후 비교  |  n=월평균 게임수, 생존율=전체 기간 누적",
         fontsize=9, ha="center", color="#888")

for idx, (code, d) in enumerate(data.items()):
    x_base = 0.03 + idx * 0.33

    # 카드 배경
    card = fig.add_axes([x_base, 0.08, 0.30, 0.80], facecolor="#F8FAFF")
    card.set_xlim(0, 10); card.set_ylim(0, 10)
    card.axis("off")

    # 국가 타이틀 바
    card.add_patch(mpatches.FancyBboxPatch((0, 8.5), 10, 1.5, boxstyle="round,pad=0.2",
                   facecolor=d["color"], edgecolor="none", alpha=0.9))
    card.text(5, 9.25, d["label"], fontsize=16, fontweight="bold", color="white",
              ha="center", va="center")

    # iOS 섹션
    card.text(5, 8.0, "iOS", fontsize=12, fontweight="bold", color="#2980B9", ha="center")

    # pre → post 큰 숫자
    ios_diff = d["ios_post"] - d["ios_pre"]
    ios_arrow = "▲" if ios_diff > 0 else "▼"
    ios_diff_color = "#2ECC71" if ios_diff > 0 else "#E74C3C"

    card.text(2.5, 7.0, f"{d['ios_pre']:.0f}%", fontsize=20, fontweight="bold",
              color="#555", ha="center", va="center")
    card.text(5, 7.0, "→", fontsize=16, color="#999", ha="center", va="center")
    card.text(7.5, 7.0, f"{d['ios_post']:.0f}%", fontsize=20, fontweight="bold",
              color=d["color"], ha="center", va="center")

    # 변화량
    card.text(5, 6.0, f"{ios_arrow} {abs(ios_diff):.1f}%p", fontsize=13, fontweight="bold",
              color=ios_diff_color, ha="center", va="center")

    # n수
    card.text(2.5, 5.4, f"n={d['ios_n_pre']}", fontsize=8, color="#999", ha="center")
    card.text(7.5, 5.4, f"n={d['ios_n_post']}", fontsize=8, color="#999", ha="center")

    # 구분선
    card.plot([1, 9], [5.0, 5.0], color="#E0E0E0", lw=1)

    # AOS 섹션
    card.text(5, 4.5, "Android", fontsize=12, fontweight="bold", color="#27AE60", ha="center")

    aos_diff = d["aos_post"] - d["aos_pre"]
    aos_arrow = "▲" if aos_diff > 0 else "▼"
    aos_diff_color = "#2ECC71" if aos_diff > 0 else "#E74C3C"

    card.text(2.5, 3.5, f"{d['aos_pre']:.0f}%", fontsize=20, fontweight="bold",
              color="#555", ha="center", va="center")
    card.text(5, 3.5, "→", fontsize=16, color="#999", ha="center", va="center")
    card.text(7.5, 3.5, f"{d['aos_post']:.0f}%", fontsize=20, fontweight="bold",
              color=d["color"], ha="center", va="center")

    card.text(5, 2.5, f"{aos_arrow} {abs(aos_diff):.1f}%p", fontsize=13, fontweight="bold",
              color=aos_diff_color, ha="center", va="center")

    card.text(2.5, 1.9, f"n={d['aos_n_pre']}", fontsize=8, color="#999", ha="center")
    card.text(7.5, 1.9, f"n={d['aos_n_post']}", fontsize=8, color="#999", ha="center")

    # 기간 레이블
    card.text(2.5, 1.2, "'22-'24", fontsize=9, color="#999", ha="center", fontweight="bold")
    card.text(7.5, 1.2, "'25~", fontsize=9, color="#999", ha="center", fontweight="bold")

    # 카드 테두리
    card.add_patch(mpatches.FancyBboxPatch((0, 0), 10, 10, boxstyle="round,pad=0.2",
                   facecolor="none", edgecolor="#DDD", lw=1.5))

# 하단 주석
fig.text(0.5, 0.02,
    "신규진입 = 각 연도 1월 TOP100 기준, 2~12월 첫 진입 | 생존 = 진입월+3개월 시점 TOP100 존재 | 매월 1일 기준 | 출처: Sensor Tower",
    fontsize=7.5, ha="center", color="#AAA")

buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", facecolor="white")
plt.close(fig)

out = "C:/Users/NHN/Documents/sensortower_api/output/S14_생존율_국가별_대시보드.png"
with open(out, "wb") as f:
    f.write(buf.getvalue())
print(f"Done: {out}")
