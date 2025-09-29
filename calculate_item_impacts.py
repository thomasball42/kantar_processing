import numpy as np
import pandas as pd
from pandas import DataFrame
from numpy import ndarray

matrix_df: DataFrame = pd.read_csv("data/product_breakdown_matrix.csv", index_col=0)
matrix_df.drop(columns=["nan"], inplace=True)
matrix_indices: list = matrix_df.index.tolist()
matrix_columns: list = matrix_df.columns.tolist()
matrix: np.ndarray = matrix_df.to_numpy(dtype=float)


impacts: DataFrame = pd.read_csv("data/food_commodity_impacts_UK.csv", index_col=0)
impacts = impacts[impacts.index.isin(matrix_columns)]
impacts.sort_index(inplace=True)

co2: ndarray   = impacts['kgCO2_per_kg'].to_numpy()
ext: ndarray   = impacts['exp_extinctions_per_kg'].to_numpy()
water: ndarray = impacts['scarcity_weighted_water_use_litres_per_kg'].to_numpy()

co2_matrix: ndarray   = np.multiply(matrix, co2)
ext_matrix: ndarray   = np.multiply(matrix, ext)
water_matrix: ndarray = np.multiply(matrix, water)

co2_sums: ndarray   = np.nansum(co2_matrix, axis=1)
ext_sums: ndarray   = np.nansum(ext_matrix, axis=1)
water_sums: ndarray = np.nansum(water_matrix, axis=1)

vals: ndarray = np.c_[co2_sums, ext_sums, water_sums]
vals = np.where(vals==0, np.nan, vals)  # replace 0 with NaN

out_df:DataFrame = pd.DataFrame(vals, index=matrix_indices, columns=["kgCO2_per_item", "exp_extinctions_per_item", "scarcity_weighted_water_use_litres_per_item"])

out_df.to_csv("data/item_impacts.csv")