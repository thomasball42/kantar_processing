import pandas as pd
import numpy as np


# Some rst codes correspond to a single item, while some are composite items
# load the mapping of RST tags

rst_to_comp_or_single_mappings = pd.read_csv('data/mappings/tag_mapping.csv')
rst_to_comp_or_single_mappings["mapped_tag"] = rst_to_comp_or_single_mappings["mapped_tag"].str.lstrip('*')

# as some rst_4_extended are NaN, we need to create a new column rst_4_lowest
# some rst_4_lowest are not unique so we create a "unique_category" column to map the tags

correct_df = pd.read_csv('data/attr_all_fixed.csv', encoding='cp1252', low_memory=False)
correct_df["rst_4_lowest"] = correct_df["rst_4_extended"].fillna(correct_df["rst_4_sub_market"])
correct_df["unique_category"] = pd.concat([correct_df["rst_4_market"],
                                           correct_df["rst_4_sub_market"],
                                           correct_df["rst_4_lowest"]],
                                           axis=1).agg(' | '.join, axis=1)

rst_to_comp_or_single_mappings["unique_category"] = pd.concat([rst_to_comp_or_single_mappings["rst_4_market"],
                                                               rst_to_comp_or_single_mappings["rst_4_sub_market"],
                                                               rst_to_comp_or_single_mappings["rst_4_lowest"]],
                                                               axis=1).agg(' | '.join, axis=1)


# this creates a attr_all_fixed_mapped.csv file with the mapped_tag column added

correct_df["mapped_tag"] = correct_df["unique_category"].map(
    rst_to_comp_or_single_mappings.set_index("unique_category")["mapped_tag"])

correct_df = correct_df.drop(columns=["rst_4_lowest", "unique_category", "Impact_category"])
correct_df.to_csv('data/attr_all_fixed_mapped.csv', index=False, encoding='cp1252')