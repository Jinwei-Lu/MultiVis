import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
n_movies = 15
data = {
    'Title': [f'Movie {i}' for i in range(1, n_movies + 1)],
    'IMDB_Rating': np.random.uniform(6, 10, n_movies)
}
df = pd.DataFrame(data)

df_sorted = df.sort_values('IMDB_Rating', ascending=False).head(10)
df_sorted = df_sorted.reset_index(drop=True)

fig, ax = plt.subplots()

cmap = plt.get_cmap('viridis')
norm = plt.Normalize(df_sorted['IMDB_Rating'].min(), df_sorted['IMDB_Rating'].max())
colors = cmap(norm(df_sorted['IMDB_Rating']))

ax.bar(df_sorted['Title'], df_sorted['IMDB_Rating'], color=colors)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
fig.colorbar(sm, ax=ax)

plt.xticks(rotation=45, ha='right')

plt.show()