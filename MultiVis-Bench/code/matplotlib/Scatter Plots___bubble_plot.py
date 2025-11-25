import matplotlib.pyplot as plt
import numpy as np

n = 400
horsepower = np.random.randint(50, 250, size=n)
miles_per_gallon = np.random.randint(10, 50, size=n) - 0.1 * horsepower
acceleration = np.random.uniform(8, 25, size=n)

plt.scatter(horsepower, miles_per_gallon, s=acceleration * 5)

plt.xlabel('Horsepower')
plt.ylabel('Miles_per_Gallon')

plt.show()