import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(0)

years = np.arange(1970, 1981)
data = []
for year in years:
    mpg_mean = 20 + (year - 1970) * 0.5
    mpg_std = 3
    mpg_values = np.random.normal(mpg_mean, mpg_std, 50)
    for mpg in mpg_values:
        data.append({'Year': year, 'Miles_per_Gallon': mpg})

source = pd.DataFrame(data)

mean_mpg = source.groupby('Year')['Miles_per_Gallon'].mean()
std_mpg = source.groupby('Year')['Miles_per_Gallon'].std()

plt.fill_between(years, mean_mpg - std_mpg, mean_mpg + std_mpg, alpha=0.5)
plt.plot(years, mean_mpg)

plt.xlabel('Year')
plt.ylabel('Miles/Gallon')

plt.legend()

plt.show()