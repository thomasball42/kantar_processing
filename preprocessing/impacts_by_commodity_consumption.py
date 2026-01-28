import numpy as np
import pandas as pd
from pandas import DataFrame
from numpy import ndarray 

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
    # print(pop)
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
                'Total' : "#000000"
                }

    # load the data from the product breakdown matrix as a matrix
    matrix_df: DataFrame = pd.read_csv("data/product_breakdown_matrix.csv", index_col=0)
    matrix_df.drop(columns=["nan"], inplace=True)
    matrix_indices: list = matrix_df.index.tolist() # PRODUCT CODES
    matrix_columns: list = matrix_df.columns.tolist()

    dat_th = pd.read_csv("data/dat_th.csv")
    
    dat_th, population = crop_valid_houses(dat_th)
    
    purchases = dat_th.groupby("product")['packs'].sum()
    purchase_index = np.asarray([purchases.loc[p] if p in purchases else 0 for p in matrix_indices])
    # print(purchases)
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
    ext_err_matrix: ndarray   = np.multiply(matrix, frac_err)


    water_matrix: ndarray = np.multiply(matrix, water)

    # sum the impacts for each item
    co2_sums: ndarray   = np.nansum(co2_matrix, axis=0)
    ext_sums: ndarray   = np.nansum(ext_matrix, axis=0)
    water_sums: ndarray = np.nansum(water_matrix, axis=0)
    ext_err_matrix[ext_err_matrix==0] = np.nan
    ext_err_sums: ndarray  = np.nanmean(ext_err_matrix, axis=0)
    ext_err_sums = ext_err_sums * ext_sums  # convert back to absolute error

    # combine the results into a dataframe and save as csv
    vals: ndarray = np.c_[consumed_masses, co2_sums, ext_sums, water_sums, ext_err_sums]
    vals = np.where(vals==0, np.nan, vals)  # replace 0 with NaN

    out_df:DataFrame = pd.DataFrame(vals, index=matrix_columns, columns=["kg", "kgCO2", "exp_extinctions", "swwu", "exp_extinctions_err"])
    out_df["exp_extinctions_per_kg"] = out_df["exp_extinctions"] / out_df["kg"]
    out_df["kgCO2_per_kg"] = out_df["kgCO2"] / out_df["kg"]
    out_df["swwu_per_kg"] = out_df["swwu"] / out_df["kg"]
    out_df["exp_extinctions_per_kg_err"] = out_df["exp_extinctions_err"] / out_df["kg"]

    out_df = out_df/(population)

    crosswalk = pd.read_csv("data/commodity_crosswalk.csv", index_col=0)
    out_df = out_df.merge(crosswalk[["group_name_v7"]], left_index=True, right_index=True, how="left")
    
    out_df.to_csv("data/category_impacts.csv")

    # print(out_df[out_df.group_name_v7.isna()])
    

    fao_impacts = pd.read_csv("data/food_commodity_impacts.csv", index_col=0)[["primary_tonnage"]]
    fao_impacts.primary_tonnage = fao_impacts.primary_tonnage*1000 / (365*67026292)
   
    mandala_impacts = out_df[["kg", "group_name_v7"]].reset_index()
    

    mandala_impacts = mandala_impacts.merge(fao_impacts, left_on="index", right_index=True, how="left")


    mandala_impacts = mandala_impacts.merge(pd.DataFrame(color_dict.items(), columns=["group_name_v7", "color"]), on="group_name_v7", how="left")
    mandala_impacts['color'] = mandala_impacts['color'].fillna("#000000")  # grey for uncategorized
    import matplotlib.pyplot as plt

    mandala_impacts.loc[mandala_impacts["index"]=="Fish", "primary_tonnage"] = 0.03834
    print(mandala_impacts.loc[mandala_impacts["index"]=="Fish"])
    plt.scatter(mandala_impacts["primary_tonnage"], mandala_impacts["kg"], c=mandala_impacts["color"])
    for commodity in mandala_impacts.index:
        plt.annotate(mandala_impacts.loc[commodity, "index"], # pyright: ignore[reportArgumentType]
                    (mandala_impacts.loc[commodity, "primary_tonnage"], mandala_impacts.loc[commodity, "kg"]), # pyright: ignore[reportArgumentType]
                    textcoords="offset points",
                    xytext=(0,10),
                    ha='center',
                    color=mandala_impacts.loc[commodity, "color"],
                    fontsize=8)

    print(mandala_impacts["primary_tonnage"].sum())

    plt.scatter([mandala_impacts["primary_tonnage"].sum()], [mandala_impacts["kg"].sum()], c="#000000",)

    plt.annotate("Total", # pyright: ignore[reportArgumentType]
                (mandala_impacts["primary_tonnage"].sum(), mandala_impacts["kg"].sum()), # pyright: ignore[reportArgumentType]
                textcoords="offset points",
                xytext=(0,10),
                ha='center',
                color="#000000",
                fontsize=8)


  

    xlim = plt.xlim()
    ylim = plt.ylim()
    # m, b = np.polyfit(mandala_impacts["primary_tonnage"], mandala_impacts["kg"], 1)
    # x = np.arange(0, xlim[1], xlim[1]/100)
    # plt.plot(x, m * x + b, color="black", linestyle="--", label=f"Line of best fit: y = {m:.4f} x + {b:.4f}")
    # print(m, b)
    for k, v in color_dict.items():
        plt.scatter([], [], c=v, label=k)
    plt.legend()
    # plt.xlim(0, xlim[1])
    # plt.ylim(0, ylim[1])
    plt.xscale("log")
    plt.yscale("log")
    plt.grid()
    plt.xlabel("FAO-based consumption (kg per capita per day)")
    plt.ylabel("WP2-based consumption (kg per capita per day)")
    plt.show()
    
    
    




if __name__ == "__main__":
    import os
    os.chdir("../")
    main()