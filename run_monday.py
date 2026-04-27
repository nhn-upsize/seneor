"""
4/6일 마스터 실행 스크립트
실행: python run_monday.py

순서:
  Step 1. v2 데이터 수집 (US 추가 + publisher_country + custom_tags)
  Step 2. PPT 슬라이드 업데이트 (슬라이드 15/16/17 → 각 2개로 분리)
"""
import subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from pathlib import Path

BASE = Path("C:/Users/NHN/Documents/sensortower_api")


def run(script_path: str, label: str):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    start = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=str(BASE),
        capture_output=False,   # 실시간 출력
    )
    elapsed = round(time.time() - start, 1)
    if result.returncode != 0:
        print(f"\n[오류] {label} 실패 (종료코드 {result.returncode})")
        print("→ 오류를 확인하고 다시 실행하거나 Step 2만 단독 실행하세요.")
        return False
    print(f"\n[완료] {label}  ({elapsed}s)")
    return True


def main():
    print("▶ 4/6일 전체 실행 시작")
    print("  예상 소요: 30~60분 (API 호출 포함)")
    print()

    # ── Step 1: 데이터 수집 ──────────────────────────────────────────────────
    ok = run(
        str(BASE / "analysis" / "collect_all_v2.py"),
        "Step 1: v2 데이터 수집 (KR/JP/US/CN + publisher_country + custom_tags)"
    )
    if not ok:
        print("\n[안내] Step 1 실패 시 기존 CSV로 Step 2를 실행합니다.")
        answer = input("Step 2(PPT 업데이트)만 계속 진행할까요? (y/n): ").strip().lower()
        if answer != "y":
            print("중단합니다.")
            return

    # ── Step 2: PPT 업데이트 ─────────────────────────────────────────────────
    ok2 = run(
        str(BASE / "analysis" / "update_ppt_slides.py"),
        "Step 2: PPT 슬라이드 업데이트 (15/16/17 → 각 2개 + 2025 전후 비교)"
    )
    if not ok2:
        return

    # ── 완료 ─────────────────────────────────────────────────────────────────
    out_pptx = BASE / "MobileGame_Market_Analysis_2022-2026_v2.pptx"
    print(f"\n{'='*60}")
    print("  전체 완료!")
    print(f"  결과 파일: {out_pptx.name}")
    print(f"  위치: {out_pptx.parent}")
    print(f"{'='*60}")
    print()
    print("생성된 슬라이드 구성:")
    print("  슬라이드 15  — 신규 게임 3개월 생존율 개요 (기존)")
    print("  슬라이드 16  — 신규 게임 3개월 생존율 — 국가별 × 2025 전후")
    print("  슬라이드 17  — 신규 게임 3개월 생존율 — 퍼블리셔별 × 2025 전후")
    print("  슬라이드 18  — 유저 잔존율 개요 (기존)")
    print("  슬라이드 19  — 유저 잔존율 — 국가별 × 2025 전후")
    print("  슬라이드 20  — 유저 잔존율 — 퍼블리셔별 × 2025 전후")
    print("  슬라이드 21  — 월 매출 개요 (기존)")
    print("  슬라이드 22  — 순위별 월 평균 매출 — 국가별 × 2025 전후")
    print("  슬라이드 23  — 순위별 월 평균 매출 — 퍼블리셔별 × 2025 전후")


if __name__ == "__main__":
    main()
