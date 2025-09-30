import pandas as pd
import numpy as np
from pandas import DataFrame, Series

# create the product matrix for all items in dat_th.csv


# calculate weights
def weight_calc(sizes:Series, units:Series, volumes:Series, packs:Series) -> list:
    weights:list = [size/1000 if unit in ['g', 'Drained weightg', 'ml'] # assume ml = g
                else volume/pack # fall back to per pack volume if mass data is unavailable
                for size, unit, volume, pack in zip(sizes, units, volumes, packs) ]
    return weights

def compute_unique_item_weights(dat_df:DataFrame) -> pd.DataFrame:
    dat_df.drop_duplicates(['product'], inplace=True)
    dat_df['item_weight_kg'] = weight_calc(dat_df['pack_size'], dat_df['pack_unit'], dat_df['volume'], dat_df['packs'])
    return dat_df


# create matrix of item weights
def create_item_weights_matrix(unique_item_properties:DataFrame, comp_matrix:DataFrame) -> DataFrame:
    comp_matrix = comp_matrix.drop("OLIVES") # there are olives as composite which we ignore in favour of olives as single item
    comp_matrix.index = comp_matrix.index.str.lower()


    matrix: np.ndarray = np.zeros((unique_item_properties.shape[0], comp_matrix.shape[1]))
    indices: list      = []
    columns: list      = comp_matrix.columns.tolist()
    
    for index, s in enumerate(unique_item_properties.itertuples()):
        product: str           = s[1]
        mapped_tag: str|float  = str(s[2]).lower()
        item_weight_kg: float  = s[3]

        indices.append(product)
        mapped_tag = np.nan if mapped_tag == 'nan' else mapped_tag

        matrix[index] = comp_matrix.loc[mapped_tag]/100 * item_weight_kg


    output_df: DataFrame = pd.DataFrame(matrix, index=indices, columns=columns)
    return output_df


def main() -> None:
    df: DataFrame = pd.read_csv('data/attr_all_fixed_mapped.csv', encoding='cp1252', low_memory=False)
    df = df[['product', 'mapped_tag']]

    dat_df: DataFrame = pd.read_csv('data/dat_th.csv', encoding='cp1252', low_memory=False)
    dat_df = compute_unique_item_weights(dat_df)

    dat_df['mapped_tag'] = dat_df['product'].map(df.set_index('product')['mapped_tag'])
    unique_item_properties = dat_df[['product', 'mapped_tag', 'item_weight_kg']]

    comp_matrix: DataFrame = pd.read_csv('data/composition_matrix.csv', encoding='cp1252', low_memory=False, index_col=0)
    out_df = create_item_weights_matrix(unique_item_properties, comp_matrix)
    out_df.to_csv('data/product_breakdown_matrix.csv', encoding='cp1252')
    

if __name__ == "__main__":
    main()