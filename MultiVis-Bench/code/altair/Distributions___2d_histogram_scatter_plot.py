import altair as alt
import numpy as np
import pandas as pd

np.random.seed(0)
imdb_ratings = np.random.normal(7, 1, 1000)
rotten_tomatoes_ratings = np.random.normal(60, 20, 1000)

imdb_bins = np.linspace(imdb_ratings.min(), imdb_ratings.max(), 10)
rotten_tomatoes_bins = np.linspace(rotten_tomatoes_ratings.min(), rotten_tomatoes_ratings.max(), 10)

hist, xedges, yedges = np.histogram2d(imdb_ratings, rotten_tomatoes_ratings, bins=(imdb_bins, rotten_tomatoes_bins))

x_centers = (xedges[:-1] + xedges[1:]) / 2
y_centers = (yedges[:-1] + yedges[1:]) / 2
X, Y = np.meshgrid(x_centers, y_centers)

x_flat = X.flatten()
y_flat = Y.flatten()
size_flat = hist.T.flatten()

df = pd.DataFrame({
    'IMDB_Rating': x_flat,
    'Rotten_Tomatoes_Rating': y_flat,
    'count': size_flat
})

chart = alt.Chart(df).mark_circle().encode(
    x='IMDB_Rating:Q',
    y='Rotten_Tomatoes_Rating:Q',
    size='count:Q'
)

chart