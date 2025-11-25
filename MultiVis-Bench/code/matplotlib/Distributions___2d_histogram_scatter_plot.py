import matplotlib.pyplot as plt
import numpy as np

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

plt.scatter(x_flat, y_flat, s=size_flat * 10, alpha=0.7)

plt.show()