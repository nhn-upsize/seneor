import sys, re, pathlib
sys.stdout.reconfigure(encoding="utf-8")
base = pathlib.Path("C:/Users/NHN/Documents/sensortower_api/pptx_unpacked3/ppt/slides")
for f in sorted(base.glob("slide*.xml")):
    texts = re.findall(r"<a:t>([^<]+)</a:t>", f.read_text(encoding="utf-8"))
    print(f"{f.name}: {texts[:4]}")
