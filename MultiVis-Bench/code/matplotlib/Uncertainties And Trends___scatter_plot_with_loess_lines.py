import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess

np.random.seed(1)

source = pd.DataFrame({
    'x': np.arange(100),
    'A': np.random.randn(100).cumsum(),
    'B': np.random.randn(100).cumsum(),
    'C': np.random.randn(100).cumsum(),
})

categories = ['A', 'B', 'C']

for category in categories:
    plt.scatter(source['x'], source[category], label=category)
    lowess_smoothed = lowess(source[category], source['x'], frac=0.3)
    plt.plot(lowess_smoothed[:, 0], lowess_smoothed[:, 1])

plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()