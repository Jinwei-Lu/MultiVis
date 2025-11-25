import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame({
    "data": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             2, 2, 2,
             3, 3,
             4, 4, 4, 4, 4, 4]
})

def rank_within_group(df, group_col, rank_col):
    df[rank_col] = df.groupby(group_col).cumcount() + 1
    return df

source = rank_within_group(source, 'data', 'id')

fig, ax = plt.subplots()

unique_data = source['data'].unique()
max_ranks = source.groupby('data')['id'].max()

for data_val in unique_data:
    subset = source[source['data'] == data_val]
    ax.scatter(subset['data'], subset['id'])

ax.set_xticks(unique_data)
ax.set_ylim(max(max_ranks) + 1, 0)
ax.set_yticks([])

plt.show()