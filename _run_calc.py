import sys; sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np

df = pd.read_csv('C:/Users/NHN/Documents/sensortower_api/app_tags.csv')
print('publisher_group 종류:', df['publisher_group'].unique())
print('총 앱 수:', len(df))
print()

# 퍼블리셔별 광고집행율
grp = df.groupby('publisher_group').agg(
    n=('app_id','count'),
    disp_ww=('paid_display_pct_ww','mean'),
    srch_ww=('paid_search_pct_ww','mean'),
    disp_us=('paid_display_pct_us','mean'),
    srch_us=('paid_search_pct_us','mean'),
).round(1)
print('=== 퍼블리셔별 광고집행율 ===')
print(grp.to_string())
print()

# 퍼블리셔별 월단위 잔존율 (D30=M1, D60=M2, D90=M3, D180=M6, D365=M12)
ret_cols = ['d30_ret_ww','d60_ret_ww','d90_ret_ww','d180_ret_ww','d365_ret_ww']
ret = df.groupby('publisher_group')[ret_cols].mean().round(1)
ret.columns = ['M+1','M+2','M+3','M+6','M+12']
print('=== 퍼블리셔별 월단위 잔존율 (WW) ===')
print(ret.to_string())
