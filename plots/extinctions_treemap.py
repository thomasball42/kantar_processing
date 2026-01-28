import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# matrix_df = pd.read_csv("data/product_breakdown_matrix.csv", index_col=0)
# matrix_df.drop(columns=["nan"], inplace=True)
# matrix_df = matrix_df.loc[165714].sum()
# print(matrix_df)
fig, ax1 = plt.subplots(figsize=(12,12))


prod_data = pd.read_csv("../data/attr_all_fixed_mapped.csv", low_memory=False)[["product", "long_desc", "rst_4_extended"]]



hh_to_exclude = []
with open("../data/hh_to_exclude.txt", "r") as f:
    for line in f:
        hh_to_exclude.append(int(line.strip()))



df = pd.read_csv("../data/dat_th_with_impacts.csv")
df = df[~df['house'].isin(hh_to_exclude)]
df = df.merge(prod_data, on='product', how='left')


people_data = pd.read_csv("../data/pan_th_new.csv")[["house", "size"]]

pop = 0
for d in df['house'].unique():
    pop += people_data[people_data['house'] == d]['size'].iloc[0]
print(f"Total population: {pop}")

def weight_calc(sizes, units, volumes, packs) -> list:
    weights:list = [size/1000 if unit in ['g', 'Drained weightg', 'ml'] # assume ml = g
                else volume/pack # fall back to per pack volume if mass data is unavailable
                for size, unit, volume, pack in zip(sizes, units, volumes, packs) ]
    return weights
df['item_weight_kg'] = weight_calc(df['pack_size'], df['pack_unit'], df['volume'], df['packs'])
df['purchased_mass_kg'] = df['item_weight_kg'] * df['packs']

plotting_categories = pd.read_csv("../data/mappings/plotting_categories.csv")

df = df.merge(plotting_categories, on='mapped_tag', how='left')
t1_colors = {
    "Beverage" : "#1156d6",
"Fruits, Vegetables and Nuts" : "#00a800",
"Cereals and Bread" : "#976801",
"Snacks and Desserts" : "#31CBF1",
# "Desserts" : "#e072d2",
"Kitchen Accessories" : "#000000",
"Prepared Foods" : "#faae3d",
"Dairy, Eggs, Meat and Plant-based Alternatives" : "#ee2424",
} 

for k, v in t1_colors.items():
    ax1.scatter([], [], color=v, label=k)
ax1.legend(loc='upper right')

display_cat = 't3_category'
display_opt = pd.read_csv("../data/mappings/display_options.csv")
for cat in df[display_cat].unique():
    sub_df = df[df[display_cat] == cat]

    if sub_df.empty or cat in ["Fish & Seafood", "Stuffing"]:
        continue
    purchased_mass = sub_df['purchased_mass_kg'].sum()
    total_extinctions = sub_df['exp_extinctions'].sum()
    per_kg_extinctions = total_extinctions / purchased_mass if purchased_mass > 0 else 0

    c = t1_colors[sub_df['t1_category'].iloc[0]] if sub_df['t1_category'].iloc[0] in t1_colors else "#888888"

    mean_daily_mass = (purchased_mass/pop)/399 # data collection ran for 399 days
    
df = df.groupby([display_cat, "t1_category"])['exp_extinctions'].sum().reset_index()
print(df)

import plotly.express as px
fig = px.treemap(df, path=['t1_category', display_cat], values='exp_extinctions',
                 color='t1_category',
                 color_discrete_map=t1_colors,
                 title="Extinctions by Food Category"
                )
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25), showlegend=True)

    # if cat == "Beef":
    #     sdf = sub_df.drop_duplicates(subset=['long_desc'])
    #     for a in sdf[["long_desc", "mapped_tag", "rst_4_extended"]].values:
    #         print(a)
    #     print(len(sdf), len(sub_df))
        # print(sub_df.long_desc.unique())
        


fig.show()
