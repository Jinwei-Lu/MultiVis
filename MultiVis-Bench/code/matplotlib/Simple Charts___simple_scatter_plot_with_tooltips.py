import matplotlib.pyplot as plt
import numpy as np

horsepower = np.random.uniform(50, 250, 100)
miles_per_gallon = 35 - horsepower / 10 + np.random.normal(0, 3, 100)
origins = np.random.choice(['USA', 'Europe', 'Japan'], 100)

unique_origins = np.unique(origins)

for i, origin in enumerate(unique_origins):
    origin_indices = origins == origin
    plt.scatter(horsepower[origin_indices], miles_per_gallon[origin_indices],
                s=60,
                label=origin)

plt.xlabel('Horsepower')
plt.ylabel('Miles_per_Gallon')
plt.legend()
plt.show()