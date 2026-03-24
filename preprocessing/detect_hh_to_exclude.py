import pandas as pd
import numpy as np
# REMOVE HOUSEHOLDS WITH LESS THAN 50 WEEKS OF DATA

def parse(week:int) -> int:
    if week > 202400:
        week -= 48
    week -= 202324
    return week
hh_data = pd.read_csv("../data/pan_th_new.csv")[["house", "size"]]
df = pd.read_csv("../data/dat_th.csv")
hh_to_exclude = []
spends = []
cals = []

for hh in df['house'].unique():
    hh_df:pd.DataFrame = df[df['house']==hh]
    min = hh_df['week'].min()
    max = hh_df['week'].max()
    delta = parse(max) - parse(min)
    if delta < 50:
        hh_to_exclude.append(hh)
    else:
        size = hh_data[hh_data['house']==hh]['size'].values[0]

        cal = (hh_df['kcals']*hh_df["packs"]).sum()/(7*delta*size)
        cals.append(cal)
        spend = hh_df['netspend'].sum()/(delta*size)
        spends.append(spend)

# print(spends)
print(f"Households: {len(spends):.0f}")
print(f"Mean / person: £{np.mean(spends):.2f}")
print(f"Median / person: £{np.median(spends):.2f}")
print(f"Std / person: £{np.std(spends):.2f}")

print(f"Mean Daily kcals / person: {np.mean(cals):.2f}")
print(f"Median Daily kcals / person: {np.median(cals):.2f}")
print(f"Std Daily kcals / person: {np.std(cals):.2f}")

import matplotlib.pyplot as plt
plt.hist(spends, bins=50)
plt.xlabel("Average Weekly Spend (£)")
plt.ylabel("Number of Households")
plt.show()
# with open("data/hh_to_exclude.txt", "w") as f:
#     for hh in hh_to_exclude:
#         f.write(f"{hh}\n")