import sys
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd

df = pd.read_csv('C:/Users/NHN/Documents/sensortower_api/slide1_v2.csv')
df = df[df['country'].isin(['KR','JP','US'])]
df['release_ym']   = df['release_date'].str[:7]
df['release_year'] = df['release_date'].str[:4]
df['chart_year']   = df['first_chart_month'].str[:4]
df['same_month']   = df['release_ym'] == df['first_chart_month']
df['same_year']    = df['release_year'] == df['chart_year']

print("=== B방식 전체 (첫 차트진입 기준) ===")
print(df.groupby(['country','period']).size().rename('n').to_string())

print("\n=== A방식: 출시월 == 첫진입월 ===")
print(df[df['same_month']].groupby(['country','period']).size().rename('n').to_string())

print("\n=== 출시연도 == 차트진입연도 (연도 일치) ===")
print(df[df['same_year']].groupby(['country','period']).size().rename('n').to_string())

print("\n=== KR 차트진입연도별 출시연도 분포 ===")
kr = df[df['country']=='KR']
print(kr.groupby(['chart_year','release_year']).size().rename('n').to_string())
