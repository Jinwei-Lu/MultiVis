import matplotlib.pyplot as plt
import numpy as np

imdb_ratings = np.random.normal(loc=7.0, scale=1.5, size=1000)
imdb_ratings = np.clip(imdb_ratings, 0, 10)

plt.hist(imdb_ratings, bins=10)
plt.show()