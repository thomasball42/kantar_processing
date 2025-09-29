import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

hh_to_exclude = []
with open("data/hh_to_exclude.txt", "r") as f:
    for line in f:
        hh_to_exclude.append(int(line.strip()))

impact_df: DataFrame = pd.read_csv("data/item_impacts.csv", index_col=0)

dat_th: DataFrame = pd.read_csv("data/dat_th.csv")
dat_th = dat_th[~dat_th['house'].isin(hh_to_exclude)]

dat_th["co2"] = dat_th['product'].map(impact_df['kgCO2_per_item'])*dat_th['packs']
dat_th["ext"] = dat_th['product'].map(impact_df['exp_extinctions_per_item'])*dat_th['packs']
dat_th["water"] = dat_th['product'].map(impact_df['scarcity_weighted_water_use_litres_per_item'])*dat_th['packs']

indexes = []
co2s = []
exts = []
waters = []

for hh in dat_th['house'].unique():
    hh_df:DataFrame = dat_th[dat_th['house']==hh]
    indexes.append(hh)
    co2s.append(hh_df['co2'].sum())
    exts.append(hh_df['ext'].sum())
    waters.append(hh_df['water'].sum())

impacts = pd.DataFrame(data={
    "house": indexes,
    "kgCO2_per_hh": co2s,
    "exp_extinctions_per_hh": exts,
    "scarcity_weighted_water_use_litres_per_hh": waters
})

# import the hh data and remove duplicate households - then extract the hh sizes and divide the impacts by hh_size to get per capita impacts
hh_data: DataFrame = pd.read_csv("data/pan_th_new.csv")
hh_data = hh_data.drop_duplicates(subset=['house'])
impacts['size'] = impacts['house'].map(hh_data.set_index('house')['size'])
impacts['kgCO2_per_capita'] = impacts['kgCO2_per_hh']/impacts['size']
impacts['exp_extinctions_per_capita'] = impacts['exp_extinctions_per_hh']/impacts['size']
impacts['scarcity_weighted_water_use_litres_per_capita'] = impacts['scarcity_weighted_water_use_litres_per_hh']/impacts['size']



cdict = {
    1: 'green',
    2: 'blue',
    3: 'pink',
    4: 'red',
    5: 'orange',
    6: 'yellow',
    7: 'yellow',
    8: 'yellow',
    9: 'yellow',
    10: 'yellow',
    11: 'yellow',
}

sns.scatterplot(data=impacts, x="kgCO2_per_hh", y="exp_extinctions_per_hh", hue="size", palette=cdict)
handles, labels = plt.gca().get_legend_handles_labels()
handles, labels = handles[:len(handles)-5], labels[:len(labels)-5]
labels[-1] = '6+'
plt.legend(handles, labels, title='Household Size')

plt.xscale('log')
plt.yscale('log')

plt.show()