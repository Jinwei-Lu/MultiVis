import matplotlib.pyplot as plt
import numpy as np

num_movies = 500
imdb_ratings = np.random.uniform(1, 10, num_movies)
imdb_ratings.sort()
cumulative_count = np.arange(1, num_movies + 1)

plt.fill_between(imdb_ratings, cumulative_count)
plt.plot(imdb_ratings, cumulative_count)
plt.xlabel("IMDB_Rating")
plt.ylabel("Cumulative Count")
plt.xlim(imdb_ratings.min(), imdb_ratings.max())
plt.ylim(0, cumulative_count.max())
plt.show()