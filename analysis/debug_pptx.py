import sys, zipfile, re
sys.stdout.reconfigure(encoding="utf-8")

base = "C:/Users/NHN/Documents/sensortower_api"

# 백업 파일의 slide25.xml 내용 (첫 번째 / 두 번째 occurrence)
print("=== 백업 slide25.xml 두 occurrence ===")
with zipfile.ZipFile(base + "/MobileGame_Market_Analysis_2022-2026_v2_backup.pptx", "r") as zf:
    count = 0
    for item in zf.infolist():
        if item.filename == "ppt/slides/slide25.xml":
            count += 1
            data = zf.read(item.filename)
            texts = re.findall(r"<a:t>([^<]{1,40})</a:t>", data.decode("utf-8"))
            print(f"  occurrence {count}: {texts[:4]}")

print()

# 현재 파일의 slide25.xml, slide26.xml 내용
print("=== 현재 파일 slide25/26.xml ===")
with zipfile.ZipFile(base + "/MobileGame_Market_Analysis_2022-2026_v2.pptx", "r") as zf:
    for name in ["ppt/slides/slide25.xml", "ppt/slides/slide26.xml"]:
        if name in zf.namelist():
            data = zf.read(name)
            texts = re.findall(r"<a:t>([^<]{1,40})</a:t>", data.decode("utf-8"))
            print(f"  {name}: {texts[:4]}")
        else:
            print(f"  {name}: 없음")

print()
# sldIdLst 확인
with zipfile.ZipFile(base + "/MobileGame_Market_Analysis_2022-2026_v2.pptx", "r") as zf:
    prs_xml = zf.read("ppt/presentation.xml").decode("utf-8")
    sld_ids = re.findall(r'<p:sldId[^/]*/>', prs_xml)
    print(f"sldIdLst 마지막 5개:")
    for e in sld_ids[-5:]:
        print(f"  {e}")
