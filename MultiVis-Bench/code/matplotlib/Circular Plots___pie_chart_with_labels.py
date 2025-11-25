import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame(
    {"category": ["a", "b", "c", "d", "e", "f"], "value": [4, 6, 10, 3, 7, 8]}
)

categories = source['category']
values = source['value']

plt.pie(values, labels=categories, startangle=90, counterclock=False)
plt.axis('equal')
plt.show()