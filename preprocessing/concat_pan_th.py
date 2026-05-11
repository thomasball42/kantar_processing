import pandas as pd

def main():

    pan_th_wave1 = pd.read_csv("data/WAVE1/raw/pan_th_new.csv")
    pan_th_wave2 = pd.read_csv("data/WAVE2/raw/pan_th.csv")

    pan_th = pd.concat([pan_th_wave1, pan_th_wave2], ignore_index=True)
    
    pan_th = pan_th.drop_duplicates(keep="first").reset_index(drop=True)

    pan_th.to_csv("data/pan_th_ALL.csv", index=False)
