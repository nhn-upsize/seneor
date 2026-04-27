"""결론 요약 장표 3종 생성"""
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


# ══════════════════════════════════════════════════════════════
# 1. 전체 8개 차트 핵심 메시지 한 장 요약
# ══════════════════════════════════════════════════════════════
def slide1():
    fig = plt.figure(figsize=(14, 8), facecolor="white")

    fig.text(0.5, 0.97, "모바일 게임 시장 분석 — 핵심 발견 요약", fontsize=20, fontweight="bold",
             ha="center", color="#1E2761")
    fig.text(0.5, 0.94, "매출 TOP 100 신규진입 기준  |  2022~2026.Q1  |  iOS + AOS  |  KR, JP, US", fontsize=10,
             ha="center", color="#888")

    items = [
        ("1", "생존율\n(국가별)", "#E74C3C",
         "전 시장 하락, 한국 AOS 가장 큰 낙폭(-16.5%p)\n미국 AOS만 유일하게 상승(+2.3%p)"),
        ("2", "광고집행율\n(국가별)", "#E67E22",
         "한국/일본: 생존 게임의 광고율이 미생존 대비 높음\n미국: 광고와 생존 간 상관 거의 없음"),
        ("3", "생존율\n(퍼블리셔)", "#F1C40F",
         "중화권이 물량 공세로 진입 최다, 기타(유럽 강자)\n생존율 최고. 한국 AOS post2025 19% 최하위"),
        ("4", "광고집행율\n(퍼블리셔)", "#2ECC71",
         "한국 퍼블리셔 UA 의존도 급상승(41.7%)\n일본/북미는 광고해도 생존 미보장"),
        ("5", "차트 잔존율\n(국가별)", "#1ABC9C",
         "M+12 잔존율 전 시장 한 자릿수로 급락\n장기 정착이 극도로 어려운 환경"),
        ("6", "차트 잔존율\n(퍼블리셔)", "#3498DB",
         "25년 이전 퍼블리셔별 격차 뚜렷했으나\n25년 이후 M+12 전 그룹 2~9%로 수렴"),
        ("7", "매출\n(국가별)", "#9B59B6",
         "미국 1위 매출 압도적(iOS $57M, AOS $33M)\nTOP 10 진입이 수익성의 결정적 분기점"),
        ("8", "매출\n(퍼블리셔)", "#1E2761",
         "중화권 AOS 상위권 매출 성장세\n북미 iOS 매출 규모 독보적"),
    ]

    for i, (num, title, color, desc) in enumerate(items):
        row = i // 4
        col = i % 4
        x = 0.03 + col * 0.245
        y = 0.48 - row * 0.44

        ax = fig.add_axes([x, y, 0.23, 0.40], facecolor="#FAFBFF")
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

        # 번호 원
        circle = plt.Circle((1.2, 8.2), 0.9, color=color, alpha=0.9)
        ax.add_patch(circle)
        ax.text(1.2, 8.2, num, fontsize=14, fontweight="bold", color="white", ha="center", va="center")

        # 제목
        ax.text(3.5, 8.2, title, fontsize=10, fontweight="bold", color="#1E2761", va="center")

        # 설명
        ax.text(0.5, 5.0, desc, fontsize=8.5, color="#555", va="center", linespacing=1.6)

        # 테두리
        ax.add_patch(mpatches.FancyBboxPatch((0, 0), 10, 10, boxstyle="round,pad=0.3",
                     facecolor="none", edgecolor="#DDD", lw=1.2))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    with open(f"{OUT}/Summary_1_핵심발견요약.png", "wb") as f:
        f.write(buf.getvalue())
    print("  1. 핵심 발견 요약 완료")


# ══════════════════════════════════════════════════════════════
# 2. NHN 시사점 및 대응 방향
# ══════════════════════════════════════════════════════════════
def slide2():
    fig = plt.figure(figsize=(14, 7), facecolor="white")

    fig.text(0.5, 0.97, "NHN 시사점 & 대응 방향", fontsize=20, fontweight="bold",
             ha="center", color="#1E2761")
    fig.text(0.5, 0.94, "시장 분석 기반 전략적 시사점", fontsize=10, ha="center", color="#888")

    items = [
        ("위기", "#C0392B", "#FDE8E8",
         "한국 퍼블리셔 생존율 최하위 (AOS 19%)\nM+3 이후 차트 잔존율 급감\n광고 의존도만 상승, 장기 경쟁력 약화",
         "신규 론칭 시 초기 3개월 생존 전략 필수\nM+3 이후 잔존 개선 로드맵 선행 설계\n게임 품질과 IP 경쟁력 확보 우선"),
        ("기회", "#E0A800", "#FFF8E1",
         "미국 AOS 유일한 생존율 상승 시장\n미국 1위 매출 $33M으로 최대 규모\n북미 퍼블리셔 안정적 생존력",
         "글로벌 타겟 시 미국 AOS 우선 진입 검토\nAction, Strategy 장르 중심 포트폴리오\n현지화 및 글로벌 퍼블리싱 역량 강화"),
        ("과제", "#059669", "#E8F5E9",
         "일본/기타(유럽) 퍼블리셔 장기 잔존 우위\n한국 M+12 잔존율 2~4%로 최하위\n광고만으로는 장기 생존 불가",
         "IP 기반 라이브서비스 강화\n커뮤니티 운영 고도화\nWhale 유저 리텐션 집중 전략"),
    ]

    for i, (badge, badge_color, bg_color, diagnosis, action) in enumerate(items):
        y = 0.63 - i * 0.30

        # 배지
        ax_badge = fig.add_axes([0.03, y + 0.08, 0.06, 0.06])
        ax_badge.set_xlim(0,1); ax_badge.set_ylim(0,1); ax_badge.axis("off")
        ax_badge.add_patch(mpatches.FancyBboxPatch((0,0), 1, 1, boxstyle="round,pad=0.1",
                          facecolor=badge_color, edgecolor="none"))
        ax_badge.text(0.5, 0.5, badge, fontsize=12, fontweight="bold", color="white", ha="center", va="center")

        # 현황 진단
        ax_left = fig.add_axes([0.10, y, 0.40, 0.18], facecolor=bg_color)
        ax_left.set_xlim(0,10); ax_left.set_ylim(0,10); ax_left.axis("off")
        ax_left.text(0.3, 9, "현황 진단", fontsize=9, fontweight="bold", color="#999")
        ax_left.text(0.3, 5, diagnosis, fontsize=9, color="#333", va="center", linespacing=1.5)
        ax_left.add_patch(mpatches.FancyBboxPatch((0,0), 10, 10, boxstyle="round,pad=0.3",
                         facecolor="none", edgecolor="#DDD", lw=1))

        # 대응 방향
        ax_right = fig.add_axes([0.52, y, 0.45, 0.18], facecolor="#F0FFF0")
        ax_right.set_xlim(0,10); ax_right.set_ylim(0,10); ax_right.axis("off")
        ax_right.text(0.3, 9, "대응 방향", fontsize=9, fontweight="bold", color="#999")
        ax_right.text(0.3, 5, action, fontsize=9, color="#059669", va="center", linespacing=1.5)
        ax_right.add_patch(mpatches.FancyBboxPatch((0,0), 10, 10, boxstyle="round,pad=0.3",
                         facecolor="none", edgecolor="#DDD", lw=1))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    with open(f"{OUT}/Summary_2_NHN시사점.png", "wb") as f:
        f.write(buf.getvalue())
    print("  2. NHN 시사점 완료")


# ══════════════════════════════════════════════════════════════
# 3. 국가별/퍼블리셔별 종합 스코어카드
# ══════════════════════════════════════════════════════════════
def slide3():
    fig = plt.figure(figsize=(14, 8.5), facecolor="white")

    fig.text(0.5, 0.97, "종합 스코어카드 — 국가별 & 퍼블리셔별", fontsize=20, fontweight="bold",
             ha="center", color="#1E2761")
    fig.text(0.5, 0.94, "25년 이후 기준  |  iOS + AOS 종합  |  매출 TOP 100 신규진입", fontsize=10,
             ha="center", color="#888")

    # 국가별 스코어카드
    fig.text(0.5, 0.90, "— 국가별 —", fontsize=12, fontweight="bold", ha="center", color="#1E2761")

    countries = [
        ("KR 한국", "#E74C3C", [
            ("생존율", "iOS 24% / AOS 22%", "▼"),
            ("M+12 잔존", "iOS 4% / AOS 4%", "▼▼"),
            ("1위 매출", "iOS $5.8M / AOS $21M", "→"),
            ("종합", "경쟁 최고, 생존 최저", ""),
        ]),
        ("JP 일본", "#2ECC71", [
            ("생존율", "iOS 25% / AOS 25%", "▼"),
            ("M+12 잔존", "iOS 12% / AOS 7%", "▼"),
            ("1위 매출", "iOS $19.6M / AOS $12.7M", "▼"),
            ("종합", "장기 잔존 강자였으나 하락", ""),
        ]),
        ("US 미국", "#3498DB", [
            ("생존율", "iOS 33% / AOS 41%", "→/▲"),
            ("M+12 잔존", "iOS 7% / AOS 6%", "▼"),
            ("1위 매출", "iOS $52.4M / AOS $33M", "▲"),
            ("종합", "매출 최대, AOS 생존 유일 상승", ""),
        ]),
    ]

    for ci, (name, color, metrics) in enumerate(countries):
        x = 0.03 + ci * 0.33
        ax = fig.add_axes([x, 0.52, 0.30, 0.36], facecolor="#FAFBFF")
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

        # 헤더
        ax.add_patch(mpatches.FancyBboxPatch((0, 8.5), 10, 1.5, boxstyle="round,pad=0.2",
                     facecolor=color, edgecolor="none", alpha=0.9))
        ax.text(5, 9.25, name, fontsize=14, fontweight="bold", color="white", ha="center", va="center")

        for mi, (label, value, trend) in enumerate(metrics):
            y = 7.0 - mi * 1.8
            trend_color = "#2ECC71" if "▲" in trend else "#E74C3C" if "▼" in trend else "#999"

            ax.text(0.5, y, label, fontsize=9, fontweight="bold", color="#999")
            ax.text(0.5, y - 0.9, value, fontsize=10, fontweight="bold" if mi == 3 else "normal",
                    color="#1E2761" if mi == 3 else "#555")
            if trend:
                ax.text(9.5, y - 0.5, trend, fontsize=12, color=trend_color, ha="right", va="center")

        ax.add_patch(mpatches.FancyBboxPatch((0, 0), 10, 10, boxstyle="round,pad=0.2",
                     facecolor="none", edgecolor="#DDD", lw=1.5))

    # 퍼블리셔별 스코어카드
    fig.text(0.5, 0.48, "— 퍼블리셔별 —", fontsize=12, fontweight="bold", ha="center", color="#1E2761")

    publishers = [
        ("한국", "#E74C3C", "생존 19~24%\nM+12 2~4%\n광고 의존 급증", "최하위"),
        ("일본", "#2ECC71", "생존 22~23%\nM+12 7~8%\n광고 없이도 생존", "장기 잔존 강자"),
        ("북미", "#3498DB", "생존 22~30%\nM+12 6~9%\n매출 규모 1위", "매출 최강"),
        ("중화권", "#F39C12", "생존 25~27%\nM+12 5~8%\n물량 공세 최다", "진입 최다"),
        ("기타", "#9B59B6", "생존 38~42%\nM+12 6~19%\nSupercell/King", "소수 정예 최강"),
    ]

    for pi, (name, color, desc, tag) in enumerate(publishers):
        x = 0.02 + pi * 0.196
        ax = fig.add_axes([x, 0.05, 0.18, 0.38], facecolor="#FAFBFF")
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

        ax.add_patch(mpatches.FancyBboxPatch((0, 8.5), 10, 1.5, boxstyle="round,pad=0.2",
                     facecolor=color, edgecolor="none", alpha=0.9))
        ax.text(5, 9.25, name, fontsize=12, fontweight="bold", color="white", ha="center", va="center")

        ax.text(5, 5.5, desc, fontsize=8.5, color="#555", ha="center", va="center", linespacing=1.5)

        ax.add_patch(mpatches.FancyBboxPatch((1.5, 0.5), 7, 1.5, boxstyle="round,pad=0.2",
                     facecolor=color, edgecolor="none", alpha=0.15))
        ax.text(5, 1.25, tag, fontsize=10, fontweight="bold", color=color, ha="center", va="center")

        ax.add_patch(mpatches.FancyBboxPatch((0, 0), 10, 10, boxstyle="round,pad=0.2",
                     facecolor="none", edgecolor="#DDD", lw=1.2))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    with open(f"{OUT}/Summary_3_종합스코어카드.png", "wb") as f:
        f.write(buf.getvalue())
    print("  3. 종합 스코어카드 완료")


if __name__ == "__main__":
    print("결론 요약 장표 생성 중...")
    slide1()
    slide2()
    slide3()
    print("\nDone!")
