import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Read the CSV file

purchases = pd.read_csv("../data/dat_th.csv")[["house", "product", "packs"]]
# purchases = pd.DataFrame(dat_th.groupby("product")['packs'].sum())

matrix_df = pd.read_csv("../data/product_breakdown_matrix.csv", index_col=0)
matrix_df.drop(columns=["nan"], inplace=True)
matrix_df = pd.DataFrame(matrix_df.sum(axis=1), columns=["mass"])

purchases = purchases.merge(matrix_df, left_on="product", right_index=True, how='left')

purchases['total_mass'] = purchases['packs'] * purchases['mass']
purchases = purchases[['house', 'total_mass']]
purchases = purchases.groupby('house').sum()

hh_data = pd.read_csv("../data/pan_th_new.csv", index_col=0)[["size"]]
hh_data = hh_data.loc[~hh_data.index.duplicated(keep='first'), :]
purchases = purchases.merge(hh_data, left_index=True, right_on="house", how='left')
purchases['mass_per_person'] = purchases['total_mass'] / purchases['size']




days = pd.read_csv("../data/dat_th.csv")[["week", "day", "packs", "house"]]
days['date'] = days['week'].astype(str) + days['day'].astype(str)
days['date'] = pd.to_datetime(days['date'], format=f'%G%V%u')
days["min_date"] = days.groupby("house")["date"].transform("min")
days["max_date"] = days.groupby("house")["date"].transform("max")
days = days[['house', 'min_date', 'max_date']].drop_duplicates()
days['days_active'] = (days['max_date'] - days['min_date']).dt.days + 1 # pyright: ignore[reportAttributeAccessIssue]
days = days.merge(hh_data, on="house", how='left').dropna(subset=['size'])
t = 395
d = days[['house', 'days_active', 'size']]
valid_houses = d[d.days_active>t]["house"]


# print(d)
# print(d["size"].sum())
# print(d[d.days_active>t]["size"].sum())
# print(d[d.days_active>t]["size"].sum()/d["size"].sum())


plt.hist(days['days_active'], weights=days['size'], bins=40, edgecolor='black')
# plt.vlines(mass/pop/399, color='red', linestyle='dashed', ymin=0, ymax=250, label=f'Average mass per capita per day: {mass/pop/399:.2f} kg')
plt.xlabel('Days')
plt.ylabel('Frequency')
# plt.ylim(0, 250)
plt.title('Purchase Days Histogram')
plt.legend()
plt.show()

purchases = purchases[purchases['house'].isin(valid_houses)]
pop = purchases['size'].sum()
mass = purchases['total_mass'].sum()
print(purchases)
# purchases = purchases[['mass_per_person']]
purchases.mass_per_person = purchases.mass_per_person / t # daily mass per person in kg
# Plot a histogram of mass per person
plt.hist(purchases['mass_per_person'], weights=purchases['size'], bins=30, edgecolor='black')
plt.vlines(mass/pop/t, color='red', linestyle='dashed', ymin=0, ymax=420, label=f'Average mass per capita per day: {mass/pop/t:.2f} kg')
plt.xlabel('Mass per Person (normalized)')
plt.ylabel('Frequency')
plt.ylim(0, 420)
plt.title('Histogram of Mass per Person (incl Water)')
plt.legend()
plt.show()