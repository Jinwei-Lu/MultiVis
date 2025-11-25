import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)

varieties = ['Manchuria', 'Glabron', 'No. 475', 'Peatland', 'Svansota', 'Velvet', 'Wisconsin No. 38']
sites = ['Grand Rapids', 'Morris', 'University Farm', 'Waseca', 'Crookston', 'Duluth']

data = []
for variety in varieties:
    for site in sites:
        for _ in range(np.random.randint(1, 5)):
            data.append({
                'variety': variety,
                'site': site,
                'year': np.random.randint(1928, 1932),
                'yield': np.random.randint(20, 50)
            })

source = pd.DataFrame(data)

alt.Chart(source).mark_bar().encode(
    x='sum(yield)',
    y='variety',
    color='site'
)