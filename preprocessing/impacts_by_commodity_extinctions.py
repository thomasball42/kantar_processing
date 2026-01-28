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

    crosswalk = pd.read_csv("data/commodity_crosswalk.csv", index_col=0)
    out_df = out_df.merge(crosswalk[["group_name_v7"]], left_index=True, right_index=True, how="left")
    
    out_df.to_csv("data/category_impacts.csv")


    

    fao_impacts = pd.read_csv("data/MAPSPAM_impacts.csv", index_col=0)[["Group", "bd_opp_total", "bd_opp_total_err"]].groupby("Group").sum()
    fao_impacts.columns = ["fao_bd_opp_total", "fao_bd_opp_total_err"]
    fao_impacts.fao_bd_opp_total = fao_impacts.fao_bd_opp_total / (365*67026292)
    fao_impacts.fao_bd_opp_total_err = fao_impacts.fao_bd_opp_total_err / (365*67026292)


    mandala_impacts = out_df[["group_name_v7", "exp_extinctions", "exp_extinctions_err"]].groupby("group_name_v7").sum()

    mandala_impacts = mandala_impacts.merge(fao_impacts, left_index=True, right_index=True, how="left")
    mandala_impacts = mandala_impacts.merge(pd.DataFrame(color_dict.items(), columns=["Group", "color"]), left_index=True, right_on="Group", how="left")

    import matplotlib.pyplot as plt
    print(mandala_impacts[["fao_bd_opp_total", "exp_extinctions", "exp_extinctions_err"]])
    for i in mandala_impacts.index:
        plt.errorbar(x=np.asarray(mandala_impacts.loc[i, "fao_bd_opp_total"]),
                    y=np.asarray(mandala_impacts.loc[i, "exp_extinctions"]),
                    xerr=np.asarray(mandala_impacts.loc[i, "fao_bd_opp_total_err"]),
                    yerr=np.asarray(mandala_impacts.loc[i, "exp_extinctions_err"]),
                    c=mandala_impacts.loc[i, "color"], capsize=5, fmt='o')
    
    xlim = plt.xlim()
    ylim = plt.ylim()
    # plt.scatter(mandala_impacts["fao_bd_opp_total"], mandala_impacts["exp_extinctions"], c=mandala_impacts["color"])
    x = np.log10(mandala_impacts["fao_bd_opp_total"])
    y = np.log10(mandala_impacts["exp_extinctions"])


    m, b = np.polyfit(x, y, 1)

    # Fit a line in log-log space
    log_x = np.log10(mandala_impacts["fao_bd_opp_total"])
    log_y = np.log10(mandala_impacts["exp_extinctions"])
    m, b = np.polyfit(log_x, log_y, 1)

    # Generate the line of best fit
    fit_x = np.logspace(-13, -9)
    fit_y = 10**(m * np.log10(fit_x) + b)
    plt.plot(fit_x, fit_y, color="black", linestyle="--", label=f"Line of best fit: log_10(y) = {m:.4f} * log_10(x) {b:.4f}")

    for k, v in color_dict.items():
        plt.scatter([], [], c=v, label=k)
    plt.legend()
    plt.xlim(2e-12, xlim[1])
    plt.ylim(5e-13, ylim[1])
    plt.xscale("log")
    plt.yscale("log")
    plt.grid()
    plt.xlabel("FAO-based biodiversity impact (daily extinctions per person)")
    plt.ylabel("WP2-based biodiversity impact (daily extinctions per person)")
    plt.show()
    print(m, b)
    
    
    




if __name__ == "__main__":
    import os
    os.chdir("../")
    main()