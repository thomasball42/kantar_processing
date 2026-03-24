import numpy as np
import pandas as pd
from pandas import DataFrame
from numpy import ndarray
import matplotlib.pyplot as plt

def crop_valid_houses(purchases: DataFrame):
    hh_data = pd.read_csv("data/pan_th_new.csv", index_col=0)[["size"]]
    hh_data = hh_data.loc[~hh_data.index.duplicated(keep='first'), :]
    purchases = purchases.merge(hh_data, left_index=True, right_on="house", how='left')
    days = pd.read_csv("data/dat_th.csv")[["week", "day", "packs", "house"]]
    days['date'] = days['week'].astype(str) + days['day'].astype(str)
    days['date'] = pd.to_datetime(days['date'], format=f'%G%V%u')
    days["min_date"] = days.groupby("house")["date"].transform("min")
    days["max_date"] = days.groupby("house")["date"].transform("max")
    days = days[['house', 'min_date', 'max_date']].drop_duplicates()
    days['days_active'] = (days['max_date'] - days['min_date']).dt.days + 1 # pyright: ignore[reportAttributeAccessIssue]
    t = 365
    d = days[['house', 'days_active']]
    d = d.merge(hh_data, on="house", how='left').dropna(subset=['size'])
    valid_houses = d[d.days_active>t]["house"]
    purchases = purchases[purchases['house'].isin(valid_houses)]
    purchases = purchases.merge(d, on="house", how='left').dropna(subset=['days_active'])
    purchases.packs = purchases.packs / purchases.days_active  # daily packs per household
    pop = d[d.days_active>t]['size'].sum()
    print(pop)
    return purchases, pop


def main():

    color_dict = {'Grains, roots, starchy carbohydrates' : "#E69F00",
                'Legumes, beans, nuts' : "#F0E442",
                'Fruit and vegetables' : "#009E73",
                'Stimulants and spices' : "#56B4E9",
                'Ruminant meat' : "#D55E00", 
                'Dairy and eggs' : "#0072B2",
                'Poultry and pig meat' : "#CC79A7", 
                'Sugar crops' : "#93F840",
                }

    # load the data from the product breakdown matrix as a matrix
    matrix_df: DataFrame = pd.read_csv("data/product_breakdown_matrix.csv", index_col=0)
    matrix_df.drop(columns=["nan"], inplace=True)
    matrix_indices: list = matrix_df.index.tolist() # PRODUCT CODES
    matrix_columns: list = matrix_df.columns.tolist()

    dat_th = pd.read_csv("data/dat_th.csv")
    dat_th, population = crop_valid_houses(dat_th)
    population = 67668790
    purchases = dat_th.groupby("product")['packs'].sum()
    purchase_index = np.asarray([purchases.loc[p] if p in purchases else 0 for p in matrix_indices])

    matrix: np.ndarray = matrix_df.to_numpy(dtype=float)

    # load the impact factors as vector
    impacts: DataFrame = pd.read_csv("data/food_commodity_impacts.csv", index_col=0)
    impacts = impacts[impacts.index.isin(matrix_columns)]
    impacts.sort_index(inplace=True)

    co2: ndarray   = impacts['kgCO2_per_kg'].to_numpy()
    ext: ndarray   = impacts['exp_extinctions_per_kg'].to_numpy()
    ext_err: ndarray   = impacts['exp_extinctions_err_per_kg'].to_numpy()
    frac_err = ext_err / ext
    frac_err = np.where(np.isnan(frac_err), 0, frac_err)  # replace NaN with 0
    water: ndarray = impacts['scarcity_weighted_water_use_litres_per_kg'].to_numpy()

    matrix = matrix * purchase_index.reshape(-1, 1)

    consumed_masses = np.nansum(matrix, axis=0)

    # use vector multiplication to calculate the impacts for each item component
    co2_matrix: ndarray   = np.multiply(matrix, co2)
    ext_matrix: ndarray   = np.multiply(matrix, ext)
    ext_err_matrix: ndarray   = np.multiply(ext_matrix, frac_err)


    water_matrix: ndarray = np.multiply(matrix, water)

    # sum the impacts for each item
    co2_sums: ndarray   = np.nansum(co2_matrix, axis=0)
    ext_sums: ndarray   = np.nansum(ext_matrix, axis=0)
    water_sums: ndarray = np.nansum(water_matrix, axis=0)
    ext_err_matrix[ext_err_matrix==0] = np.nan
    ext_err_sums: ndarray  = np.nansum(ext_err_matrix, axis=0)
    # ext_err_sums = ext_err_sums * ext_sums  # convert back to absolute error

    # combine the results into a dataframe and save as csv
    vals: ndarray = np.c_[consumed_masses, co2_sums, ext_sums, water_sums, ext_err_sums]
    vals = np.where(vals==0, np.nan, vals)  # replace 0 with NaN

    out_df:DataFrame = pd.DataFrame(vals, index=matrix_columns, columns=["kg", "kgCO2", "exp_extinctions", "swwu", "exp_extinctions_err"])
    out_df["exp_extinctions_per_kg"] = out_df["exp_extinctions"] / out_df["kg"]
    out_df["kgCO2_per_kg"] = out_df["kgCO2"] / out_df["kg"]
    out_df["swwu_per_kg"] = out_df["swwu"] / out_df["kg"]
    out_df["exp_extinctions_per_kg_err"] = out_df["exp_extinctions_err"] / out_df["kg"]

    out_df = out_df/(population)
    # print(out_df[["kg", "exp_extinctions", "exp_extinctions_per_kg"]], ext)
    out_df["exp_extinctions_per_kg"] = impacts["exp_extinctions_per_kg"]

    crosswalk = pd.read_csv("data/commodity_crosswalk.csv", index_col=0)
    out_df = out_df.merge(crosswalk[["group_name_v7"]], left_index=True, right_index=True, how="left")
    
    out_df.to_csv("data/category_impacts.csv")
    
    out_df = out_df.merge(pd.DataFrame.from_dict(color_dict, orient='index', columns=['color']), left_on='group_name_v7', right_index=True, how='left')
    out_df['color'] = out_df['color'].fillna("#808080")  # grey for uncategorized
    print(out_df)
    impacts = impacts.merge(crosswalk[["group_name_v7"]], left_index=True, right_index=True, how="left")
    impacts = impacts.merge(pd.DataFrame.from_dict(color_dict, orient='index', columns=['color']), left_on='group_name_v7', right_index=True, how='left')
    fig, ax1 = plt.subplots(figsize=(12,12))
    impacts["color"] = impacts["color"].fillna("#808080")  # grey for uncategorized
    impacts = impacts[~impacts.index.isin(["Butter, Cream & Ghee", "Cheese"])]
    ax1.scatter(impacts["primary_tonnage"]*(1000/(365*population)), impacts["exp_extinctions_per_kg"], c=impacts["color"])
    for commodity in impacts.index:
        ax1.annotate(commodity,
                     (float(impacts.loc[commodity, "primary_tonnage"])*(1000/(365*population)), impacts.loc[commodity, "exp_extinctions_per_kg"]), # pyright: ignore[reportArgumentType]
                     textcoords="offset points",
                     xytext=(0,10),
                     ha='center',
                     color=out_df.loc[commodity, "color"],
                     fontsize=8)
    

    total_kg = impacts["primary_tonnage"].sum()*(1000/(365*population))
    impacts["exp_extinctions"] = impacts["exp_extinctions_per_kg"] * impacts["primary_tonnage"] * 1000 
    total_ext_per_kg = impacts["exp_extinctions"].sum() / total_kg
    ax1.scatter(total_kg, total_ext_per_kg, color="#000000", s=100, marker="x", label="Total")
    ax1.annotate("Total",
                 (total_kg, total_ext_per_kg), # pyright: ignore[reportArgumentType]
                 textcoords="offset points",
                 xytext=(0,10),
                 ha='center',
                 color="#000000",
                 fontsize=10,
                 fontweight='bold')

    for k, v in color_dict.items():
        ax1.scatter([], [], color=v, label=k)
    ax1.legend(loc='lower left')   




    total_grid_color = "#2F7FF8"

    for i in [1e-18, 1e-17, 1e-16, 1e-15, 1e-14, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8]:
        x = np.logspace(-6, 1, 50)
        y = i/x
        ax1.plot(x, y, color=total_grid_color, alpha=0.4, linewidth=0.8)

    for j in range(-18, -8):
        for i in np.linspace(1*(10**j), 9*(10**j), 9):
            
            x = np.logspace(-6, 1, 50)
            y = i/x
            ax1.plot(x, y, ls="dashed", color=total_grid_color, alpha=0.2, linewidth=0.8)




    ax1.set_ylim(1e-13, 1e-8)
    ax1.set_xlim(1e-6, 1)
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
    
    plt.savefig("outputs/commodities_scatter.png", dpi=300, bbox_inches='tight')
    # plt.show()


    
    




if __name__ == "__main__":
    import os
    os.chdir("../")
    main()