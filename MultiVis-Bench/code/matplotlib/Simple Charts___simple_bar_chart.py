import matplotlib.pyplot as plt
import pandas as pd

data = {
    'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
}
df = pd.DataFrame(data)

plt.bar(df['a'], df['b'])
plt.show()