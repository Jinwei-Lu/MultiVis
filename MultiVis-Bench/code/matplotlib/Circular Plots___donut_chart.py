import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame({
    "category": [1, 2, 3, 4, 5, 6],
    "value": [4, 6, 10, 3, 7, 8]
})

categories = source['category']
values = source['value']

plt.pie(values, labels=categories, startangle=90, wedgeprops=dict(width=0.4))

centre_circle = plt.Circle((0, 0), 0.6, color='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.axis('equal')

plt.show()