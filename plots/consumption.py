import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# matrix_df = pd.read_csv("data/product_breakdown_matrix.csv", index_col=0)
# matrix_df.drop(columns=["nan"], inplace=True)
# matrix_df = matrix_df.loc[165714].sum()
# print(matrix_df)
fig, ax1 = plt.subplots(figsize=(20,12))


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

t1_order = {
    "Beverage" : 6,
"Fruits, Vegetables and Nuts" : 8,
"Cereals and Bread" : 3,
"Snacks and Desserts" : 5,
# "Desserts" : 4,
"Kitchen Accessories" : 2,
"Prepared Foods" : 1,
"Dairy, Eggs, Meat and Plant-based Alternatives" : 7,
} 

for k, v in t1_colors.items():
    ax1.scatter([], [], color=v, label=k)
ax1.legend(loc='lower right')

df["t4_category"] = df["t2_category"].fillna(df["t3_category"])



display_cat = 't4_category'
mean_daily_mass = df.groupby(display_cat)['purchased_mass_kg'].sum()/(pop*399)

t1 = df.groupby(display_cat)["t1_category"].first()

df2 = pd.concat([mean_daily_mass, t1], axis=1).reset_index()

# print(df2.reset_index())

# df2 = pd.DataFrame(mean_daily_mass, columns=["ex"]).reset_index()
# df2["t1_category"] = t1.values
# print(df2)

df2["c"] = df2["t1_category"].map(t1_colors)
df2["o"] = df2["t1_category"].map(t1_order)
df2.sort_values(by="purchased_mass_kg", inplace=True)
df2.sort_values(by=["o", "purchased_mass_kg"], inplace=True)
df2.dropna(subset=["purchased_mass_kg"], inplace=True)
print(df2)
df2 = df2[df2["t4_category"] != "Fish & Seafood"]

ax1.scatter(df2["t4_category"], df2['purchased_mass_kg'], color=df2['c'])


 


# ax1.set_ylim(3e-13, 1e-9)
# ax1.set_ylim(0, 5e-10)
ax1.set_yscale('log')
ax1.set_xlabel(u"Category")
ax1.set_ylabel(u"Per Capita mean daily purchased mass (kg)")
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90, ha='right')

plt.savefig("../outputs/consumption_scatter.png", dpi=300, bbox_inches='tight')
# plt.show()