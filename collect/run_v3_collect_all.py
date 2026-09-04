"""
v3 전체 데이터 재수집 마스터 실행 스크립트
실행: python analysis/run_v3_collect_all.py [--from PART번호]

PART 1  iOS  slide1_v2.csv        신규게임 생존율 재수집 (topgrossing)
PART 2  iOS  slide2_v2.csv        신규게임 잔존율 d1~d365 재수집
PART 3  iOS  newgame_ad_rates.csv 신규게임 광고율 재수집
PART 4  AOS  slide1_v2_android.csv 신규게임 생존율 (이미 topgrossing)
PART 5  AOS  slide2_v2_android.csv 신규게임 잔존율 d1~d365 재수집
PART 6  AOS  newgame_ad_rates_android.csv 신규게임 광고율 신규수집
PART 7  AOS  slide3_rank_revenue_android.csv 순위별 매출 신규수집
"""
import sys, subprocess, argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from pathlib import Path

BASE = Path("C:/Users/NHN/Documents/sensortower_api")
ANA  = BASE / "analysis"

PARTS = {
    1: ("iOS slide1+slide2 재수집 (topgrossing, d1~d365)",
        [sys.executable, str(ANA/"collect_all_v2.py"), "--part", "1"]),
    2: ("iOS 신규게임 광고율 재수집",
        [sys.executable, str(ANA/"collect_newgame_ad_rates.py")]),
    3: ("AOS slide1 재수집 (생존율)",
        [sys.executable, str(ANA/"collect_android_data.py"), "--part", "4"]),
    4: ("AOS slide2 재수집 (잔존율 d1~d365)",
        [sys.executable, str(ANA/"collect_android_data.py"), "--part", "2"]),
    5: ("AOS 신규게임 광고율 신규수집",
        [sys.executable, str(ANA/"collect_android_data.py"), "--part", "5"]),
    6: ("AOS 순위별 매출 신규수집",
        [sys.executable, str(ANA/"collect_slide3_android.py")]),
}

def run(part_num: int, desc: str, cmd: list):
    print(f"\n{'='*60}")
    print(f"▶ PART {part_num}: {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=str(BASE))
    if result.returncode != 0:
        print(f"\n⚠ PART {part_num} 실패 (returncode={result.returncode})")
        print("  계속 진행하려면 Enter, 중단하려면 Ctrl+C")
        try:
            input()
        except KeyboardInterrupt:
            sys.exit(1)
    else:
        print(f"\n✔ PART {part_num} 완료")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="from_part", type=int, default=1,
                        help="시작할 PART 번호 (기본=1)")
    parser.add_argument("--only", type=int, default=None,
                        help="특정 PART만 실행")
    args = parser.parse_args()

    print("=" * 60)
    print("v3 전체 데이터 재수집 시작")
    print(f"총 {len(PARTS)}개 PART / 예상 API 호출: ~1,050건")
    print("=" * 60)

    for part_num, (desc, cmd) in PARTS.items():
        if args.only is not None:
            if part_num != args.only:
                continue
        else:
            if part_num < args.from_part:
                print(f"  PART {part_num} 건너뜀 (--from {args.from_part})")
                continue
        run(part_num, desc, cmd)

    print("\n" + "=" * 60)
    print("✔ 전체 수집 완료!")
    print("다음 단계: python analysis/rebuild_all_charts.py")
    print("=" * 60)
