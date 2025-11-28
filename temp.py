import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('data/pan_th_new.csv')

# Assume 'sex' column has values like 'Male' and 'Female' (adjust if needed)
# Create age bins
age_bins = np.arange(0, 101, 5)  # 0-100 in 5-year bins
df['age_group'] = pd.cut(df['age'], bins=age_bins, right=False)

# Group by age_group and sex, count frequencies
grouped = df.groupby(['age_group', 'sex']).size().unstack(fill_value=0)

# Prepare data for pyramid: males negative, females positive
if 'Male' in grouped.columns and 'Female' in grouped.columns:
    males = -grouped['Male']
    females = grouped['Female']
else:
    # Adjust column names if different (e.g., 'M' and 'F')
    print("Adjust column names for 'sex' if not 'Male' and 'Female'")
    males = -grouped.iloc[:, 0]  # Assuming first column is males
    females = grouped.iloc[:, 1]  # Assuming second is females

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(grouped.index.astype(str), males, color='blue', label='Male')
ax.barh(grouped.index.astype(str), females, color='red', label='Female')
ax.set_xlabel('Population')
ax.set_ylabel('Age Group')
ax.set_title('Population Pyramid by Age and Sex')
ax.legend()
ax.grid(True, axis='x')
plt.tight_layout()
plt.show()