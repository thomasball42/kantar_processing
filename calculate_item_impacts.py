import numpy as np
import pandas as pd
from pandas import DataFrame
from numpy import ndarray

# load the data from the product breakdown matrix as a matrix
matrix_df: DataFrame = pd.read_csv("data/product_breakdown_matrix.csv", index_col=0)
matrix_df.drop(columns=["nan"], inplace=True)
matrix_indices: list = matrix_df.index.tolist() # PRODUCT CODES
matrix_columns: list = matrix_df.columns.tolist()
matrix: np.ndarray = matrix_df.to_numpy(dtype=float)

# load the impact factors as vector
impacts: DataFrame = pd.read_csv("data/food_commodity_impacts_UK.csv", index_col=0)
impacts = impacts[impacts.index.isin(matrix_columns)]
impacts.sort_index(inplace=True)

co2: ndarray   = impacts['kgCO2_per_kg'].to_numpy()
ext: ndarray   = impacts['exp_extinctions_per_kg'].to_numpy()
water: ndarray = impacts['scarcity_weighted_water_use_litres_per_kg'].to_numpy()


# use vector multiplication to calculate the impacts for each item component
co2_matrix: ndarray   = np.multiply(matrix, co2)
ext_matrix: ndarray   = np.multiply(matrix, ext)
water_matrix: ndarray = np.multiply(matrix, water)

# sum the impacts for each item
co2_sums: ndarray   = np.nansum(co2_matrix, axis=1)
ext_sums: ndarray   = np.nansum(ext_matrix, axis=1)
water_sums: ndarray = np.nansum(water_matrix, axis=1)

# combine the results into a dataframe and save as csv
vals: ndarray = np.c_[co2_sums, ext_sums, water_sums]
vals = np.where(vals==0, np.nan, vals)  # replace 0 with NaN

out_df:DataFrame = pd.DataFrame(vals, index=matrix_indices, columns=["kgCO2_per_item", "exp_extinctions_per_item", "scarcity_weighted_water_use_litres_per_item"])

out_df.to_csv("data/item_impacts.csv")


recreate_dat_th: DataFrame = pd.read_csv("data/dat_th.csv")
recreate_dat_th['kgCO2_per_pack'] = recreate_dat_th['product'].map(out_df['kgCO2_per_item'])
recreate_dat_th['exp_extinctions_per_pack'] = recreate_dat_th['product'].map(out_df['exp_extinctions_per_item'])
recreate_dat_th['scarcity_weighted_water_use_litres_per_pack'] = recreate_dat_th['product'].map(out_df['scarcity_weighted_water_use_litres_per_item'])
recreate_dat_th['kgCO2'] = recreate_dat_th['kgCO2_per_pack'] * recreate_dat_th['packs']
recreate_dat_th['exp_extinctions'] = recreate_dat_th['exp_extinctions_per_pack'] * recreate_dat_th['packs']
recreate_dat_th['scarcity_weighted_water_use_litres'] = recreate_dat_th['scarcity_weighted_water_use_litres_per_pack'] * recreate_dat_th['packs']
recreate_dat_th.to_csv("data/dat_th_with_impacts.csv", index=False)
