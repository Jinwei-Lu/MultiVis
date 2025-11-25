import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 200
data = {
    'Horsepower': np.random.randint(50, 250, size=n_samples),
    'Acceleration': np.random.uniform(8, 25, size=n_samples),
    'Miles_per_Gallon': np.random.uniform(10, 50, size=n_samples),
    'Origin': np.random.choice(['USA', 'Europe', 'Japan'], size=n_samples)
}
df = pd.DataFrame(data)

rows = ['Horsepower', 'Acceleration', 'Miles_per_Gallon']
cols = ['Miles_per_Gallon', 'Acceleration', 'Horsepower']

fig, axes = plt.subplots(len(rows), len(cols))

origins = df['Origin'].unique()

for i, row_var in enumerate(rows):
    for j, col_var in enumerate(cols):
        ax = axes[i, j]
        for origin in origins:
            subset = df[df['Origin'] == origin]
            ax.scatter(subset[col_var], subset[row_var])
        
        ax.set_xlabel(col_var)
        ax.set_ylabel(row_var)

plt.show()