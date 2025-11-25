import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

np.random.seed(0)
data = {
    'petalWidth': np.random.rand(50) * 2.5,
    'petalLength': np.random.rand(50) * 6 + 1,
    'sepalWidth': np.random.rand(50) * 2 + 2,
    'sepalLength': np.random.rand(50) * 4 + 4,
}
source = pd.DataFrame(data)

df_melted = source.melt(
    value_vars=["petalWidth", "petalLength", "sepalWidth", "sepalLength"],
    var_name="Measurement_type",
    value_name="value",
)

measurement_types = df_melted["Measurement_type"].unique()
fig, axes = plt.subplots(len(measurement_types), 1, sharex=True)

x_min = 0
x_max = 8
x = np.linspace(x_min, x_max, 500)

for i, measurement in enumerate(measurement_types):
    subset = df_melted[df_melted["Measurement_type"] == measurement]
    kde = gaussian_kde(subset["value"], bw_method=0.3)
    density = kde(x)
    ax = axes[i]
    ax.plot(x, density)
    ax.fill_between(x, density, alpha=0.5)
    ax.set_ylabel("Density")
    ax.set_ylim(bottom=0)

plt.show()