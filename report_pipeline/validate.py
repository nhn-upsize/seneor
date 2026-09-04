"""
report_pipeline / validate.py
=============================
분기 보고서 HTML 의 **자기정합성(내부 일관성)을 전수 검사**한다.
DB 불필요 — HTML만 읽어서 "안 바뀐 곳/서로 안 맞는 곳"을 리스트업.

이번(2026-07) 세션에서 실제로 터진 버그류를 그대로 잡도록 설계:
  [C1] Step2 국적별 표: 메인 국적 행 == TOP5 + 기타  (모든 컬럼: 22·23·24·25·부분·전·후)
  [C2] 한눈에 카드의 전→후 == 해당국 Step2 합계의 전→후  (카드 미갱신 드리프트)

사용:  python -m report_pipeline.validate [HTML경로]
       (경로 생략 시: 저장소면 가장 최근 분기의 index.html, 로컬이면 sensor_dashboard_work.html)
반환:  불일치 0건이면 exit 0, 있으면 목록 출력 후 exit 1
"""
import re, sys
from pathlib import Path

try:                       # Windows 콘솔(cp949)에서도 한글/기호 출력
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent


def default_target():
    """검사 대상 기본값.

    1순위: 가장 최근 분기 폴더(26Y1Q, 26Y2Q, …)의 index.html  ← seneor 저장소
    2순위: sensor_dashboard_work.html                        ← 로컬 작업 폴더
    """
    dirs = sorted(
        (p for p in REPO_ROOT.glob("[0-9][0-9]Y[1-4]Q") if (p / "index.html").is_file()),
        key=lambda p: p.name,
    )
    if dirs:
        return dirs[-1] / "index.html"

    legacy = REPO_ROOT / "sensor_dashboard_work.html"
    if legacy.is_file():
        return legacy

    raise SystemExit(
        "검사할 HTML을 찾지 못했습니다. 경로를 인자로 넘겨주세요.\n"
        "  예) python -m report_pipeline.validate 26Y2Q/index.html"
    )

# 국가별 Step2 TOP5/기타 앵커. 메인 국적행은 "TOP5 행 바로 위 <tr>"로 잡아 모호성 제거.
# (동명 국적행이 KR/JP/US/3국합산 탭에 중복 존재하므로 라벨 단독 앵커는 위험)
STEP2_ROWS = {
    "KR": {"top5": "한국 TOP 5 합산", "etc": "한국 기타 (TOP 5 외)"},
    "JP": {"top5": "일본 TOP 5 합산", "etc": "일본 기타 (TOP 5 외)"},
    "US": {"top5": "북미 TOP 5 합산", "etc": "북미 기타 (TOP 5 외)"},
}
COLS = ["'22", "'23", "'24", "'25", "부분(26.1H)", "전", "후"]


def _row_html(html, anchor):
    """anchor 를 포함하는 <tr>...</tr> substring 반환 (유니크 앵커용)."""
    i = html.find(anchor)
    if i < 0:
        return None
    start = html.rfind("<tr", 0, i)
    end = html.find("</tr>", i)
    return html[start:end] if start >= 0 and end >= 0 else None


def _row_before(html, anchor):
    """anchor 행의 '바로 위 <tr>' 반환 (메인 국적행 = TOP5 행 직전)."""
    i = html.find(anchor)
    if i < 0:
        return None
    top5_start = html.rfind("<tr", 0, i)
    main_end = html.rfind("</tr>", 0, top5_start)
    main_start = html.rfind("<tr", 0, main_end)
    return html[main_start:main_end] if main_start >= 0 else None


def _nums(row):
    """행에서 '숫자억' 패턴을 순서대로 뽑아 int 리스트로. (값 5 + 전 + 후 = 7개 기대)"""
    if row is None:
        return None
    return [int(x.replace(",", "")) for x in re.findall(r">\s*([\d,]+)억", row)]


def check_step2_breakdown(html):
    """[C1] 메인 == TOP5 + 기타 (모든 컬럼)."""
    issues = []
    for mkt, a in STEP2_ROWS.items():
        main = _nums(_row_before(html, a["top5"]))
        top5 = _nums(_row_html(html, a["top5"]))
        etc  = _nums(_row_html(html, a["etc"]))
        if not (main and top5 and etc):
            issues.append(f"[C1][{mkt}] 행 추출 실패 (앵커 확인): "
                          f"main={bool(main)} top5={bool(top5)} etc={bool(etc)}")
            continue
        n = min(len(main), len(top5), len(etc), len(COLS))
        for k in range(n):
            got = top5[k] + etc[k]
            diff = main[k] - got
            # 허용오차: 반올림·파이프라인 노이즈(±수억)는 통과, '셀 미갱신'급 차이만 잡음
            tol = max(12, round(main[k] * 0.005))
            if abs(diff) > tol:
                issues.append(
                    f"[C1][{mkt}] {COLS[k]}: 메인 {main[k]:,} ≠ TOP5({top5[k]:,})+기타({etc[k]:,})={got:,} "
                    f"(차이 {diff:+,}, 허용 ±{tol})")
    return issues


def check_cards_vs_totals(html):
    """[C2] 한눈에 카드 전→후 == 해당국 Step2 합계 전→후 (KR/JP만; US는 조 단위라 스킵)."""
    issues = []
    # 카드: <div class="cc-go">...: A억 → B억
    cards = {m[0]: (m[1], m[2]) for m in re.findall(
        r'country-card (\w+)".*?cc-go">25년 전후 \(월평균\): ([\d,]+)억 → ([\d,]+)억',
        html, re.S)}
    # Step2 합계 행 전→후 (KR/JP 국가패널의 합계). 국가별 합계는 '합계' 행의 <strong>A억 → B억</strong>
    for mkt in ("KR", "JP"):
        key = mkt.lower()
        if key not in cards:
            continue
        card_pre, card_post = cards[key]
        # 해당국 Step2 합계: main 국적 표의 '합계' 행. 간단히 해당국 헤드라인 h2에서 비교
        head = re.search(rf"{'한국' if mkt=='KR' else '일본'} 시장: 월평균 매출 ([\d,]+)억원 \(22~24\) → ([\d,]+)억원",
                         html)
        if head:
            h_pre, h_post = head.group(1), head.group(2)
            if (card_pre, card_post) != (h_pre, h_post):
                issues.append(
                    f"[C2][{mkt}] 카드({card_pre}→{card_post}) ≠ 헤드라인({h_pre}→{h_post})")
    return issues


CHECKS = [check_step2_breakdown, check_cards_vs_totals]


def run(html_path=None):
    path = Path(html_path) if html_path else default_target()
    html = path.read_text(encoding="utf-8")
    all_issues = []
    for chk in CHECKS:
        all_issues += chk(html)
    print(f"[validate] {path.parent.name}/{path.name} — 검사 {len(CHECKS)}종")
    if not all_issues:
        print("  ✅ 불일치 0건 (자기정합 통과)")
        return 0
    print(f"  ❌ 불일치 {len(all_issues)}건:")
    for m in all_issues:
        print("   -", m)
    return 1


if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else None))
