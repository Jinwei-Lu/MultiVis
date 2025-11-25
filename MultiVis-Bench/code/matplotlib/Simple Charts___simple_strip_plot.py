import matplotlib.pyplot as plt
import numpy as np

horsepower = np.random.randint(50, 300, size=150)
cylinders = np.random.choice([4, 6, 8], size=150)

plt.scatter(horsepower, cylinders, marker='|', s=200, linewidths=1)
plt.xlabel('Horsepower')
plt.ylabel('Cylinders')
plt.yticks([4, 6, 8], ['4', '6', '8'])

plt.show()