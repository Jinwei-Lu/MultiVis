import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

date_range = pd.date_range(start='2000-01-01', end='2010-12-31', freq='M')
num_dates = len(date_range)
prices = 100 + np.cumsum(np.random.randn(num_dates) * 5)
data = pd.DataFrame({'date': date_range, 'price': prices})

fig, ax = plt.subplots()
ax.step(data['date'], data['price'], where='post')
plt.show()