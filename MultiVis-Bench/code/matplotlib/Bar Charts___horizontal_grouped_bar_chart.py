import matplotlib.pyplot as plt
import numpy as np
import random

years = list(range(1900, 2000, 5))
wheat_values = [random.randint(300, 700) + i*2 for i in range(len(years))]

plt.barh(y=years, width=wheat_values, height=3)
plt.yticks(years)
plt.ylabel("year")
plt.xlabel("wheat")
plt.gca().invert_yaxis()

plt.show()