import pandas as pd
import numpy as np
from numpy import ndarray
from pandas import DataFrame, Series


# use single item mapping to relate Tom and Mikes slightly different food categories to the same single item tag
single_item_mapping: DataFrame = pd.read_csv('data/mappings/single_item_mapping_with_modifier_tag.csv')
single_item_dict: dict = dict(zip(single_item_mapping['Food_Category_sub_sub'], single_item_mapping['Food Commodity']))


food_composition_df: DataFrame = pd.read_csv('data/food_group_compositions.csv')
food_composition_df["Food_Category_sub"] = food_composition_df["Food_Category_sub"].fillna(food_composition_df["Food_Category"])
food_composition_df["Food_Category_sub_sub"] = food_composition_df["Food_Category_sub_sub"].fillna(food_composition_df["Food_Category_sub"])
food_composition_df: DataFrame = food_composition_df.drop(columns=["Food_Category", "Food_Category_sub"])

food_composition_df["Tag"] = food_composition_df["Food_Category_sub_sub"].map(single_item_dict)


# collect all the unique rst market from both composite and single item tags
unique_single_tags_from_composites: ndarray|list = food_composition_df["Tag"].unique()
unique_single_tags_from_composites = [str(tag) for tag in unique_single_tags_from_composites]

rst_mapping_df: DataFrame = pd.read_csv('data/mappings/tag_mapping.csv')
unique_tags_from_rst: list = rst_mapping_df["mapped_tag"].unique().tolist()
unique_single_tags_from_rst: list = [tag[1:] for tag in unique_tags_from_rst if type(tag) == str and tag[0] == "*"]

unique_single_tags: list = sorted(list(set(unique_single_tags_from_composites).union(set(unique_single_tags_from_rst))))


# matrix setup
unique_items: ndarray = food_composition_df["validation_field_title"].unique()
single_item_array: DataFrame = pd.DataFrame(0, index=unique_items, columns=unique_single_tags)
single_item_matrix: ndarray = single_item_array.to_numpy(dtype=float)
index_map: dict = {item: idx for idx, item in enumerate(unique_items)}
column_map: dict = {tag: idx for idx, tag in enumerate(unique_single_tags)}


# converts the messy input data into a clean composition matrix
# composite items
for composite_item in food_composition_df["validation_field_title"].unique():
    composite_df: DataFrame = food_composition_df[food_composition_df["validation_field_title"] == composite_item]
    for constituent_tag in composite_df["Tag"].unique():
        constituent_df: DataFrame = composite_df[composite_df["Tag"] == constituent_tag]
        proportion: float = constituent_df["percent"].sum()
        single_item_matrix[index_map[composite_item], column_map[str(constituent_tag)]] = proportion
# single items
single_item_array: DataFrame = pd.DataFrame(single_item_matrix, index=unique_items, columns=unique_single_tags)
for item in unique_single_tags_from_rst:
    row: ndarray = np.zeros(len(unique_single_tags))
    row[column_map[item]] = 100.
    single_item_array.loc[item] = row
        
single_item_array.to_csv('data/composition_matrix.csv')
