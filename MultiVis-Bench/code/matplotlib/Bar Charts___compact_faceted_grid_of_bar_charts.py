import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame(
    [
        {"a": "a1", "b": "b1", "c": "x", "p": 0.14},
        {"a": "a1", "b": "b1", "c": "y", "p": 0.60},
        {"a": "a1", "b": "b1", "c": "z", "p": 0.03},
        {"a": "a1", "b": "b2", "c": "x", "p": 0.80},
        {"a": "a1", "b": "b2", "c": "y", "p": 0.38},
        {"a": "a1", "b": "b2", "c": "z", "p": 0.55},
        {"a": "a1", "b": "b3", "c": "x", "p": 0.11},
        {"a": "a1", "b": "b3", "c": "y", "p": 0.58},
        {"a": "a1", "b": "b3", "c": "z", "p": 0.79},
        {"a": "a2", "b": "b1", "c": "x", "p": 0.83},
        {"a": "a2", "b": "b1", "c": "y", "p": 0.87},
        {"a": "a2", "b": "b1", "c": "z", "p": 0.67},
        {"a": "a2", "b": "b2", "c": "x", "p": 0.97},
        {"a": "a2", "b": "b2", "c": "y", "p": 0.84},
        {"a": "a2", "b": "b2", "c": "z", "p": 0.90},
        {"a": "a2", "b": "b3", "c": "x", "p": 0.74},
        {"a": "a2", "b": "b3", "c": "y", "p": 0.64},
        {"a": "a2", "b": "b3", "c": "z", "p": 0.19},
        {"a": "a3", "b": "b1", "c": "x", "p": 0.57},
        {"a": "a3", "b": "b1", "c": "y", "p": 0.35},
        {"a": "a3", "b": "b1", "c": "z", "p": 0.49},
        {"a": "a3", "b": "b2", "c": "x", "p": 0.91},
        {"a": "a3", "b": "b2", "c": "y", "p": 0.38},
        {"a": "a3", "b": "b2", "c": "z", "p": 0.91},
        {"a": "a3", "b": "b3", "c": "x", "p": 0.99},
        {"a": "a3", "b": "b3", "c": "y", "p": 0.80},
        {"a": "a3", "b": "b3", "c": "z", "p": 0.37},
    ]
)

factor_a_levels = sorted(source['a'].unique())
factor_b_levels = sorted(source['b'].unique())
settings_levels = sorted(source['c'].unique())

fig, axes = plt.subplots(len(factor_a_levels), len(factor_b_levels), sharex=True, sharey=True)

for i, a_level in enumerate(factor_a_levels):
    for j, b_level in enumerate(factor_b_levels):
        ax = axes[i, j]
        subset = source[(source['a'] == a_level) & (source['b'] == b_level)]
        y_positions = [0, 1, 2]
        for k, setting in enumerate(settings_levels):
            setting_data = subset[subset['c'] == setting].iloc[0]
            ax.barh(y_positions[k], setting_data['p'], height=0.8)

plt.show()