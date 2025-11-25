import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

np.random.seed(42)
n_samples = 150
data = {
    'petalWidth': np.random.normal(1.2, 0.3, n_samples),
    'petalLength': np.random.normal(4.4, 1.0, n_samples),
    'sepalWidth': np.random.normal(3.0, 0.4, n_samples),
    'sepalLength': np.random.normal(5.8, 0.8, n_samples),
}
source = pd.DataFrame(data)

df_melted = source.melt(var_name='Measurement_type', value_name='value')

fig, ax = plt.subplots()

extent = [0, 8]
steps = 200
x_vals = np.linspace(extent[0], extent[1], steps)

for measurement_type in df_melted['Measurement_type'].unique():
    subset = df_melted[df_melted['Measurement_type'] == measurement_type]['value']
    kde = gaussian_kde(subset, bw_method=0.3)
    density = kde.evaluate(x_vals)
    density = density * len(subset)
    ax.fill_between(x_vals, density, label=measurement_type)

ax.set_xlabel('value')
ax.set_ylabel('density')
ax.set_xlim(extent)
ax.set_ylim(bottom=0)
ax.legend()

plt.show()