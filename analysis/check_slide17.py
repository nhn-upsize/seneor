import sys, zipfile, re, pathlib
sys.stdout.reconfigure(encoding="utf-8")

base = "C:/Users/NHN/Documents/sensortower_api"

# 백업 슬라이드 파일 목록
path = base + "/MobileGame_Market_Analysis_2022-2026_v2_backup.pptx"
with zipfile.ZipFile(path, "r") as zf:
    slides = sorted(set([n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]))
    print("백업 슬라이드 파일:", slides)

# pptx_unpacked3/slide17.xml 텍스트
s17 = pathlib.Path(base + "/pptx_unpacked3/ppt/slides/slide17.xml").read_text(encoding="utf-8")
texts17 = re.findall(r"<a:t>([^<]+)</a:t>", s17)
print("slide17.xml 텍스트:", texts17[:10])
