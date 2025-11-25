import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 200
horsepower = np.random.randint(50, 250, size=n_samples)
origin = np.random.choice(['USA', 'Europe', 'Japan'], size=n_samples)
df = pd.DataFrame({'Horsepower': horsepower, 'Origin': origin})

fig, axes = plt.subplots(nrows=3, sharex=True, sharey=True)

origins = df['Origin'].unique()

for i, orig in enumerate(origins):
    subset = df[df['Origin'] == orig]
    axes[i].hist(subset['Horsepower'], bins=10)

axes[-1].set_xlabel("Horsepower")

plt.show()