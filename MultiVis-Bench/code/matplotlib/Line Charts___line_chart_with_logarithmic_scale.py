import matplotlib.pyplot as plt
import numpy as np

years = np.arange(1900, 2001, 10)
people_sum = np.exp(np.linspace(10, 14, len(years)))

plt.plot(years, people_sum)
plt.xlabel('year')
plt.ylabel('sum(people)')
plt.yscale('log')

plt.show()