import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

hh_to_exclude = []
with open("data/hh_to_exclude.txt", "r") as f:
    for line in f:
        hh_to_exclude.append(int(line.strip()))

impact_df: DataFrame = pd.read_csv("data/item_impacts.csv", index_col=0)

dat_th: DataFrame = pd.read_csv("data/dat_th.csv")
dat_th = dat_th[~dat_th['house'].isin(hh_to_exclude)]

dat_th["co2"] = dat_th['product'].map(impact_df['kgCO2_per_item'])*dat_th['packs']
dat_th["ext"] = dat_th['product'].map(impact_df['exp_extinctions_per_item'])*dat_th['packs']
dat_th["water"] = dat_th['product'].map(impact_df['scarcity_weighted_water_use_litres_per_item'])*dat_th['packs']

indexes = []
co2s = []
exts = []
waters = []

for hh in dat_th['house'].unique():
    hh_df:DataFrame = dat_th[dat_th['house']==hh]
    indexes.append(hh)
    co2s.append(hh_df['co2'].sum())
    exts.append(hh_df['ext'].sum())
    waters.append(hh_df['water'].sum())

impacts = pd.DataFrame(data={
    "house": indexes,
    "kgCO2_per_hh": co2s,
    "exp_extinctions_per_hh": exts,
    "scarcity_weighted_water_use_litres_per_hh": waters
})

# import the hh data and remove duplicate households - then extract the hh sizes and divide the impacts by hh_size to get per capita impacts
hh_data: DataFrame = pd.read_csv("data/pan_th_new.csv")
hh_data['terageed'] = hh_data['terageed'].apply(lambda x: 0 if x == 9 else x) # correct for a mistake in data

hh_data['in_edu'] = hh_data['terageed'].apply(lambda x: True if x == 4 else False) # create a column for "in education"
hh_data['edu_age'] = hh_data['age']*hh_data['in_edu'] # create a column for age if in education, 0 otherwise
hh_data['edu_over_19'] = hh_data['edu_age'].apply(lambda x: True if x >= 19 else False) # create a column for if in education and over 16
hh_data.loc[hh_data['edu_over_19'], 'terageed'] = 3


hh_data['education'] = hh_data['terageed'].apply(lambda x: -1 if x == 4 else x) # set "in education" at bottom 
hh_max_edu = hh_data.groupby('house')['education'].max()
hh_data['maxeducation'] = hh_data['house'].map(hh_max_edu)
print(hh_data['maxeducation'].value_counts())
hh_data2 = hh_data.copy()


hh_data = hh_data.drop_duplicates(subset=['house'])
#hh_data = hh_data[hh_data['individ'] == 0]
impacts['size'] = impacts['house'].map(hh_data.set_index('house')['size'])
impacts['num_adult'] = impacts['house'].map(hh_data.set_index('house')['num_adult'])
impacts['class'] = impacts['house'].map(hh_data.set_index('house')['sclass'])
impacts['kgCO2_per_capita'] = impacts['kgCO2_per_hh']/impacts['size']
impacts['exp_extinctions_per_capita'] = impacts['exp_extinctions_per_hh']/impacts['size']
impacts['scarcity_weighted_water_use_litres_per_capita'] = impacts['scarcity_weighted_water_use_litres_per_hh']/impacts['size']
impacts['edu'] = impacts['house'].map(hh_data.set_index('house')['maxeducation'])


# impacts['edu2'] = impacts['house'].map(hh_data_maxeducation['terageed'])


def hist_plot(impacts, t:str='class', hh_or_capita:str='capita'):
    if hh_or_capita == 'capita':
        impacts = impacts.loc[impacts.index.repeat(impacts['size'])]


    classdict = {
        1:"AB",
        3:"C1",
        4:"C2",
        5:"D",
        6:"E"
        }
    rows = 6

    if t == 'edu':
        classdict = {
            1:"0-15",
            2:"16-18",
            3:"19+",
            -1:"Still in education"
        }
        rows=4
        #impacts = impacts[impacts['edu'] != 0]
   
    fig, t_axs = plt.subplots(rows, 2, figsize=(10, 10))
    t_axs = t_axs.flatten()
    co2_axs = t_axs[::2]
    ext_axs = t_axs[1::2]


    letter_dict = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h', 8:'i', 9:'j', 10:'k', 11:'l'}
    for i, ax in enumerate(t_axs):
        ax.text(0.95, 0.9, letter_dict[i], horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=16)
       
    
    for x, axs, lims in zip([f'kgCO2_per_{hh_or_capita}', f'exp_extinctions_per_{hh_or_capita}'], [co2_axs, ext_axs], [(0, 6000), (0, 1.2e-7)]):
        if hh_or_capita=='hh':
            lims = (lims[0]*1.5, lims[1]*1.5)

        avg_ax = axs[-1]
        axs = axs[:-1]
        for i, ax in enumerate(axs):
            if t == 'class':
                i += 2
                i = i if i != 2 else 1
            if t == 'edu':
                i += 1
            class_impacts = impacts[impacts[t]==i]
            
            sns.kdeplot(class_impacts, x=x, ax=avg_ax, label=classdict[i], levels=20)
            stop=lims[1]
            range_array = [0, 1000, 2000, 3000, 4000, 5000, 6000] if stop == 6000 else [0, 2e-8, 4e-8, 6e-8, 8e-8, 1e-7, 1.2e-7]
            ax.set_xticks(range_array, labels=[])
            mean = class_impacts[x].mean()
            # Get the y-value of the kde at the mean
            kde_lines = [line for line in avg_ax.get_lines() if line.get_label() == classdict[i]]
            if kde_lines:
                kde_line = kde_lines[0]
                xdata = kde_line.get_xdata()
                ydata = kde_line.get_ydata()
                # Find the y-value at the mean (interpolate if necessary)
                if len(xdata) > 1:
                    y_at_mean = np.interp(mean, xdata, ydata)
                else:
                    y_at_mean = 0
                avg_ax.vlines(mean, 0, y_at_mean, color=kde_line.get_color(), linestyle='-', linewidth=1, zorder=0)
                sns.histplot(class_impacts, x=x, bins=40, ax=ax, kde=True, color=kde_line.get_color())
            ax.set_xlim(lims)
            ax.set_xlabel("")
            # avg_ax.set_xticks(range_array, labels=range_array)
        avg_ax.set_yticks([])
        avg_ax.set_xlim(lims)
    t_string = 'Highest education level\nin household' if t == 'edu' else t
    t_axs[-1].legend(title=t_string, loc='center right')
    t_axs[-1].set_xlabel(rf'Per {hh_or_capita} expected extinctions')
    t_axs[-2].set_xlabel(rf'Per {hh_or_capita} CO$_2$ emissions / kg')
    fig.suptitle('Impacts of food consumption by UK households')
    fig.tight_layout()
    return impacts

def scatter_plot():

    cdict = {    1: 'green',    2: 'blue',    3: 'pink',    4: 'red',    5: 'orange',    6: 'yellow',    7: 'yellow',    8: 'yellow',    9: 'yellow',    10: 'yellow',    11: 'yellow',}
    sns.scatterplot(data=impacts, x="kgCO2_per_hh", y="exp_extinctions_per_hh", hue="size", palette=cdict)
    handles, labels = plt.gca().get_legend_handles_labels()
    handles, labels = handles[:6], labels[:6]
    labels[-1] = '6+'
    plt.legend(handles, labels, title='size')
    plt.xscale('log')
    plt.yscale('log')
    plt.show()

def box_plot_class():
    classdict = {
        1:"AB",
        3:"C1",
        4:"C2",
        5:"D",
        6:"E"
        }

    fig, axs = plt.subplots(1,2, figsize=(10,5))

    for x, ax, lims in zip(['kgCO2_per_capita', 'exp_extinctions_per_capita'], axs, [(1, 6000), (0, 1e-7)]):
        sns.boxplot(impacts, x='class', y=x, ax=ax,)
        ax.set_xticks(ticks=[0,1,2,3,4], labels=['AB', 'C1', 'C2', 'D', 'E'])
        
        # Add a line one standard deviation away from the mean for each class
        for i, label in enumerate(['AB', 'C1', 'C2', 'D', 'E']):
            class_num = list(classdict.keys())[i]
            class_impacts = impacts[impacts['class'] == class_num]
            mean = class_impacts[x].mean()
            std = class_impacts[x].std()
            ax.scatter(i, mean, color='red', zorder=5, marker='X', linewidth=0.2)
            ax.hlines(mean - std, xmin=i-0.2, xmax=i+0.2, color='gray', linestyle='--', linewidth=1)
            ax.hlines(mean + std, xmin=i-0.2, xmax=i+0.2, color='gray', linestyle='--', linewidth=1)
    fig.tight_layout()

def box_plot_edu(impacts, hh_or_capita:str='capita'):
    classdict = {
            0:"Unknown",
            1:"0-15",
            2:"16-18",
            3:"19+",
            -1:"Still in education"
        }
    impacts = impacts[impacts['edu'] != 0]
    impacts['edu'] = impacts['edu'].replace(-1, 4)
    # impacts = impacts[impacts['edu'] != 4]

    fig, axs = plt.subplots(1,2, figsize=(10,5))

    for x, ax, lims in zip([f'kgCO2_per_{hh_or_capita}', f'exp_extinctions_per_{hh_or_capita}'], axs, [(1, 6000), (0, 1e-7)]):
        sns.boxplot(impacts, x='edu', y=x, ax=ax,)
        tick_locs = [0,1,2]
        # ax.set_xticks(ticks=tick_locs, labels=["0-15", "16-18", "19+"])
        
        # Add a line one standard deviation away from the mean for each class
        for i in range(3):
            class_num = list(classdict.keys())[i]
            class_impacts = impacts[impacts['edu'] == i+1]
            mean = class_impacts[x].mean()
            std = class_impacts[x].std()
            ax.scatter(i, mean, color='red', zorder=5, marker='X', linewidth=0.2)
            ax.hlines(mean - std, xmin=i-0.2, xmax=i+0.2, color='gray', linestyle='--', linewidth=1)
            ax.hlines(mean + std, xmin=i-0.2, xmax=i+0.2, color='gray', linestyle='--', linewidth=1)
    fig.tight_layout()
    plt.show()

s = 'capita'

impacts = hist_plot(impacts, 'edu',s)
# box_plot_edu(impacts, s)
