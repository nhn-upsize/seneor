"""
"서구권" → "서구권" 일괄 변경 스크립트
대상: .py, .js, .csv 파일 (sensortower_api 폴더 내 전체)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

BASE = Path("C:/Users/NHN/Documents/sensortower_api")
OLD  = "서구권"
NEW  = "서구권"

exts = {".py", ".js", ".csv"}
total_files = 0
total_count = 0

for fpath in BASE.rglob("*"):
    if fpath.suffix not in exts:
        continue
    if ".cache" in str(fpath) or "__pycache__" in str(fpath):
        continue
    try:
        text = fpath.read_text(encoding="utf-8-sig")
    except Exception:
        try:
            text = fpath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  ⚠ 읽기 실패: {fpath.name} — {e}")
            continue

    cnt = text.count(OLD)
    if cnt == 0:
        continue

    new_text = text.replace(OLD, NEW)
    fpath.write_text(new_text, encoding="utf-8")
    print(f"  ✔ {fpath.relative_to(BASE)}  ({cnt}곳 변경)")
    total_files += 1
    total_count += cnt

print(f"\n총 {total_files}개 파일, {total_count}곳 변경 완료")
