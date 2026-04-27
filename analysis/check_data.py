import sys
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd

df2 = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/slide2_v2.csv")
post = df2[df2["period"] == "post2025"]
pre  = df2[df2["period"] == "pre2025"]

print("=== Slide18: 국가별 잔존율 ===")
print("-- 2025이전 --")
print(pre.groupby("country")[["d1","d7","d14","d30"]].mean().round(1))
print("-- 2025이후 --")
print(post.groupby("country")[["d1","d7","d14","d30"]].mean().round(1))
print("행수:", post.groupby("country").size().to_dict())

print()
print("=== Slide19: 퍼블리셔별 잔존율 ===")
print("-- 2025이전 --")
print(pre.groupby("publisher_group")[["d1","d7","d14","d30"]].mean().round(1))
print("-- 2025이후 --")
print(post.groupby("publisher_group")[["d1","d7","d14","d30"]].mean().round(1))
print("행수:", post.groupby("publisher_group").size().to_dict())
