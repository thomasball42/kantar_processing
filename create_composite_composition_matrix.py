import pandas as pd
import numpy as np


single_item_mapping = pd.read_csv('data/mappings/single_item_mapping_with_modifier_tag.csv')
single_item_dict = dict(zip(single_item_mapping['Food_Category_sub_sub'], single_item_mapping['Food Commodity']))


food_composition_df = pd.read_csv('data/food_group_compositions.csv')
food_composition_df["Food_Category_sub"] = food_composition_df["Food_Category_sub"].fillna(food_composition_df["Food_Category"])
food_composition_df["Food_Category_sub_sub"] = food_composition_df["Food_Category_sub_sub"].fillna(food_composition_df["Food_Category_sub"])
food_composition_df = food_composition_df.drop(columns=["Food_Category", "Food_Category_sub"])

food_composition_df["Tag"] = food_composition_df["Food_Category_sub_sub"].map(single_item_dict)

unique_single_tags_from_composites = food_composition_df["Tag"].unique()
unique_single_tags_from_composites = [str(tag) for tag in unique_single_tags_from_composites]

rst_mapping_df = pd.read_csv('data/mappings/tag_mapping.csv')
unique_tags_from_rst = rst_mapping_df["mapped_tag"].unique().tolist()
unique_single_tags_from_rst = [tag[1:] for tag in unique_tags_from_rst if type(tag) == str and tag[0] == "*"]

unique_single_tags = sorted(list(set(unique_single_tags_from_composites).union(set(unique_single_tags_from_rst))))



unique_items = food_composition_df["validation_field_title"].unique()
single_item_array = pd.DataFrame(0, index=unique_items, columns=unique_single_tags)
single_item_matrix = single_item_array.to_numpy(dtype=float)
index_map = {item: idx for idx, item in enumerate(unique_items)}
column_map = {tag: idx for idx, tag in enumerate(unique_single_tags)}



for composite_item in food_composition_df["validation_field_title"].unique():
    composite_df = food_composition_df[food_composition_df["validation_field_title"] == composite_item]
    for constituent_tag in composite_df["Tag"].unique():
        constituent_df = composite_df[composite_df["Tag"] == constituent_tag]
        proportion = constituent_df["percent"].sum()
        single_item_matrix[index_map[composite_item], column_map[str(constituent_tag)]] = proportion

single_item_array = pd.DataFrame(single_item_matrix, index=unique_items, columns=unique_single_tags)
for item in unique_single_tags_from_rst:
    row = np.zeros(len(unique_single_tags))
    row[column_map[item]] = 100.
    single_item_array.loc[item] = row
        
single_item_array.to_csv('data/mappings/composition_matrix.csv')
