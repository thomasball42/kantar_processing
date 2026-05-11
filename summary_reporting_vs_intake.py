import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

app_strs = ["WAVE1", "WAVE2"]
colours = ["red", "blue"]
alpha = 0.3
identifiers = [["house", "week"]]

fig, axs = plt.subplots(2, 2, figsize=(10, 7), sharex="col", sharey="col")
axs = axs.flatten()

figs_dir = Path("..", "figs")
figs_dir.mkdir(parents=True, exist_ok=True)

for a, app_str in enumerate(app_strs):
    df = pd.read_csv(f"data/{app_str}/dat_th_{app_str}_with_impacts.csv")
    df.columns = df.columns.str.lower()

    if app_str == "WAVE1":
        hh_data = pd.read_csv(f"data/{app_str}/raw/pan_th_new.csv")
    else:
        hh_data = pd.read_csv(f"data/{app_str}/raw/pan_th.csv")

    houses = df.house.dropna().drop_duplicates().unique()
    
    for h, house in enumerate(houses):
        house_data = df[df.house == house]
        
        