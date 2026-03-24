import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# matrix_df = pd.read_csv("data/product_breakdown_matrix.csv", index_col=0)
# matrix_df.drop(columns=["nan"], inplace=True)
# matrix_df = matrix_df.loc[165714].sum()
# print(matrix_df)
fig = plt.figure(figsize=(12,12))
ax1 = fig.add_axes((0.1, 0.11, 0.77, 0.77))




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



display_cat = 't2_category'
display_opt = pd.read_csv("../data/mappings/display_options.csv")

veg_df = df[df["t3_category"].isin(["Vegetables", "Root Vegetables", "Potatoes"])]
fruit_df = df[df["t3_category"] == "Fruit"]

total_grid_color = "#2F7FF8"
c1 = "#292929"
c2 = "#E62222"
for sdf, c in zip([veg_df, fruit_df], [c1, c2]):

    for cat in sdf[display_cat].unique():
        sub_df = sdf[sdf[display_cat] == cat]

        if sub_df.empty or cat in ["Fish & Seafood", "Stuffing"]:
            continue
        purchased_mass = sub_df['purchased_mass_kg'].sum()
        total_extinctions = sub_df['exp_extinctions'].sum()
        per_kg_extinctions = total_extinctions / purchased_mass if purchased_mass > 0 else 0


        mean_daily_mass = (purchased_mass/pop)/399 # data collection ran for 399 days
        if cat == "Other Tropical Fruit":
            for j in sub_df["rst_4_extended"].unique():
                print(len(sub_df[sub_df["rst_4_extended"] == j]), j)
        ax1.scatter(mean_daily_mass, per_kg_extinctions, color=c, s=10, zorder=1)
        display = display_opt[display_opt['t3_category'] == cat]['display'].iloc[0]
        location = display_opt[display_opt['t3_category'] == cat]['location'].iloc[0]
        
        z=0.9
        if display:
            z = 1.1 if location else 0.9
        ax1.text(mean_daily_mass, per_kg_extinctions * z, cat, color=c, horizontalalignment='center', verticalalignment='center', zorder=2)
            


    for i in range(-16, -5):
        i = 10 ** (i)
        x = np.logspace(-5, 1, 50)
        y = i/x
        ax1.plot(x, y, color=total_grid_color, alpha=0.4, linewidth=0.8)

    for j in range(-18, -9):
        for i in np.linspace(1*(10**j), 9*(10**j), 9):
            
            x = np.logspace(-5, 1, 50)
            y = i/x
            ax1.plot(x, y, ls="dashed", color=total_grid_color, alpha=0.2, linewidth=0.8)

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel(u"Mean Daily Purchased Mass (kg)", fontsize=12)
ax1.set_ylabel(u"Extinctions per kg (kg$^{-1}$)", fontsize=12)
ax1.grid(True, which="major", linewidth=0.5)


ax1.set_ylim(1e-12, 1e-9)
ax1.set_xlim(7e-5, 1e-1)


ax1.scatter([], [], color=c2, label='Fruit')
ax1.scatter([], [], color=c1, label='Vegetables')
ax1.legend(frameon=False, loc='upper right', fontsize=12)


axb = ax1.twiny()
axb.set_xscale('log')
x1, x2 = ax1.get_xlim()
y1, y2 = ax1.get_ylim()
axb.set_xlim(x1*y2, x2*y2)
axb.set_xlabel("Total Daily Extinctions", color=total_grid_color, fontsize=12)
axb.tick_params(axis='x', colors=total_grid_color)




plt.savefig("../outputs/extinctions_breakdown.png", dpi=300, bbox_inches='tight')
print(ax1.get_position())
# plt.show()