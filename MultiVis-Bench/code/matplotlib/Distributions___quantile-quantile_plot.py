import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

np.random.seed(42)
n_samples = 200
data = np.random.randn(n_samples, 2)
u = data[:, 0]

p = np.linspace(0.01, 0.99, 99)
v = np.quantile(u, p)

uniform = p
normal = norm.ppf(p)

fig, axes = plt.subplots(1, 2, sharey=True)
axes[0].scatter(uniform, v)
axes[0].set_xlabel("Uniform Quantile")
axes[0].set_ylabel("v")

axes[1].scatter(normal, v)
axes[1].set_xlabel("Normal Quantile")

plt.show()