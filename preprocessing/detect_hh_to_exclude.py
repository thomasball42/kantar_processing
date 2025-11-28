import pandas as pd
import numpy as np
# REMOVE HOUSEHOLDS WITH LESS THAN 50 WEEKS OF DATA

def parse(week:int) -> int:
    if week > 202400:
        week -= 48
    week -= 202324
    return week


df = pd.read_csv("data/dat_th.csv")
hh_to_exclude = []

for hh in df['house'].unique():
    hh_df:pd.DataFrame = df[df['house']==hh]
    min = hh_df['week'].min()
    max = hh_df['week'].max()
    delta = parse(max) - parse(min)
    if delta < 50:
        hh_to_exclude.append(hh)

with open("data/hh_to_exclude.txt", "w") as f:
    for hh in hh_to_exclude:
        f.write(f"{hh}\n")