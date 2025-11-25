import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)

imdb_ratings = np.random.normal(loc=6.5, scale=1.5, size=1000)
rotten_tomatoes_ratings = np.random.normal(loc=60, scale=15, size=1000)

imdb_ratings = np.clip(imdb_ratings, 0, 10)
rotten_tomatoes_ratings = np.clip(rotten_tomatoes_ratings, 0, 100)

bins_x = np.linspace(0, 10, 61)
bins_y = np.linspace(0, 100, 41)

hist, xedges, yedges = np.histogram2d(imdb_ratings, rotten_tomatoes_ratings, bins=[bins_x, bins_y])

plt.imshow(hist.T, origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], aspect='auto')
plt.xlabel('IMDB Rating')
plt.ylabel('Rotten Tomatoes Rating')
plt.colorbar()

plt.show()