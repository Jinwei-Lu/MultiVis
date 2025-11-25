import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
num_points = 500

release_dates = np.random.randint(1930, 2011, num_points)
rating_deltas = []

for year in release_dates:
    if year < 1970:
        rating_delta = np.random.uniform(-1, 2)
    elif year < 1990:
        rating_delta = np.random.uniform(-2, 2.5)
    else:
        rating_delta = np.random.uniform(-4, 3)
    rating_deltas.append(rating_delta)

df = pd.DataFrame({'Release Date': release_dates, 'Rating Delta': rating_deltas})

scatter = plt.scatter(df['Release Date'], df['Rating Delta'], c=df['Rating Delta'])
plt.xlabel('Release Date')
plt.ylabel('Rating Delta')
plt.xlim(1928, 2012)
plt.ylim(-5, 3)
plt.colorbar(scatter)

plt.show()