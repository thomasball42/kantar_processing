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
    
    ax1.scatter(mean_daily_mass, per_kg_extinctions, color=c, s=10, zorder=1)
    display = display_opt[display_opt['t3_category'] == cat]['display'].iloc[0]
    location = display_opt[display_opt['t3_category'] == cat]['location'].iloc[0]
    
    z=0.93
    if display:
        z = 1.07 if location else 0.93
        ax1.text(mean_daily_mass, per_kg_extinctions * z, cat, color=c, horizontalalignment='center', verticalalignment='center', zorder=2)


    # if cat == "Beef":
    #     sdf = sub_df.drop_duplicates(subset=['long_desc'])
    #     for a in sdf[["long_desc", "mapped_tag", "rst_4_extended"]].values:
    #         print(a)
    #     print(len(sdf), len(sub_df))
        # print(sub_df.long_desc.unique())
        

T_ext = df['exp_extinctions'].sum()
T_mass = df['purchased_mass_kg'].sum()
T_ext_per_kg = T_ext / T_mass
T_daily_mass_per_person = T_mass / (pop * 399)  # data collection ran for 399 days
ax1.scatter(T_daily_mass_per_person, T_ext_per_kg, color="#444444", s=10)
ax1.text(T_daily_mass_per_person, T_ext_per_kg * 0.93, "Total", color="#444444", horizontalalignment='center', verticalalignment='center')
print(T_ext/pop)

total_grid_color = "#2F7FF8"

for i in [1e-15, 1e-14, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9]:
    x = np.logspace(-4, 1, 50)
    y = i/x
    ax1.plot(x, y, color=total_grid_color, alpha=0.4, linewidth=0.8)

for j in range(-16, -9):
    for i in np.linspace(1*(10**j), 9*(10**j), 9):
        
        x = np.logspace(-4, 1, 50)
        y = i/x
        ax1.plot(x, y, ls="dashed", color=total_grid_color, alpha=0.2, linewidth=0.8)




ax1.set_ylim(3e-13, 1e-9)
ax1.set_xlim(1e-4, 2e0)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel(u"Mean Daily Purchased Mass (kg)")
ax1.set_ylabel(u"Extinctions per kg (kg$^{-1}$)")
ax1.grid(True, which="major", linewidth=0.5)

ax2 = ax1.twiny()
ax2.set_xscale('log')
x1, x2 = ax1.get_xlim()
y1, y2 = ax1.get_ylim()
ax2.set_xlim(x1*y2, x2*y2)
ax2.set_xlabel("Total Daily Extinctions", color=total_grid_color)
ax2.tick_params(axis='x', colors=total_grid_color)

plt.savefig("outputs/extinctions.png", dpi=300, bbox_inches='tight')
# plt.show()