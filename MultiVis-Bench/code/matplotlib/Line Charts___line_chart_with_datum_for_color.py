import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
imdb_rating = np.random.rand(100) * 10
us_gross = np.random.rand(100) * 1000 + imdb_rating * 50
worldwide_gross = np.random.rand(100) * 2000 + imdb_rating * 100

bins = np.linspace(0, 10, 11)
digitized = np.digitize(imdb_rating, bins)

us_gross_means = []
worldwide_gross_means = []
bin_centers = []

for i in range(1, len(bins)):
    bin_indices = digitized == i
    if np.any(bin_indices):
        us_gross_means.append(np.mean(us_gross[bin_indices]))
        worldwide_gross_means.append(np.mean(worldwide_gross[bin_indices]))
        bin_centers.append((bins[i - 1] + bins[i]) / 2)

fig, ax = plt.subplots()

ax.plot(bin_centers, us_gross_means, label='US_Gross')
ax.plot(bin_centers, worldwide_gross_means, label='Worldwide_Gross')

ax.set_xlabel('IMDB_Rating (Binned)')
ax.set_ylabel('Mean of US and Worldwide Gross')
ax.legend()

plt.show()