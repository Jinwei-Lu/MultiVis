import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = [
    {"label": "Begin", "amount": 4000},
    {"label": "Jan", "amount": 1700},
    {"label": "Feb", "amount": -1400},
    {"label": "Mar", "amount": -1000},
    {"label": "Apr", "amount": 1800},
    {"label": "May", "amount": -1100},
    {"label": "Jun", "amount": -1500},
    {"label": "Jul", "amount": 1200},
    {"label": "Aug", "amount": 1200},
    {"label": "Sep", "amount": 1100},
    {"label": "Oct", "amount": 1200},
    {"label": "Nov", "amount": -1400},
    {"label": "Dec", "amount": 1500},
    {"label": "End", "amount": 0},
]
source = pd.DataFrame(data)

source['window_sum_amount'] = source['amount'].cumsum()
source['calc_prev_sum'] = source['window_sum_amount'].shift(1).fillna(0)
source.loc[source['label'] == 'End', 'calc_prev_sum'] = 0

source['calc_amount'] = source['amount']
source.loc[source['label'] == 'End', 'calc_amount'] = source['window_sum_amount']
source['calc_text_amount'] = source['calc_amount'].apply(lambda x: f"+{x}" if x > 0 and x != source['amount'].iloc[0] else str(x))

source['calc_center'] = (source['window_sum_amount'] + source['calc_prev_sum']) / 2
source['calc_sum_dec'] = np.where(source['window_sum_amount'] < source['calc_prev_sum'], source['window_sum_amount'], np.nan)
source['calc_sum_inc'] = np.where(source['window_sum_amount'] > source['calc_prev_sum'], source['window_sum_amount'], np.nan)
source['calc_lead'] = source['label'].shift(-1).fillna(source['label'].iloc[-1])

fig, ax = plt.subplots()

for i, row in source.iterrows():
    color = "gray" if row['label'] in ("Begin", "End") else ("green" if row['calc_amount'] < 0 else "red")
    ax.bar(row['label'], row['window_sum_amount'] - row['calc_prev_sum'], bottom=row['calc_prev_sum'], color=color)

for i, row in source.iterrows():
    if row['label'] != 'End':
        ax.plot([row['label'], row['calc_lead']], [row['window_sum_amount'], row['window_sum_amount']], color='black')

for i, row in source.iterrows():
    if not pd.isna(row['calc_sum_inc']):
        ax.text(row['label'], row['calc_sum_inc'], f"{int(row['calc_sum_inc'])}", ha='center', va='bottom')
    if not pd.isna(row['calc_sum_dec']):
        ax.text(row['label'], row['calc_sum_dec'], f"{int(row['calc_sum_dec'])}", ha='center', va='top')
    ax.text(row['label'], row['calc_center'], row['calc_text_amount'], ha='center', va='center', color='white')

ax.set_xlabel("Months")
ax.set_ylabel("Amount")
plt.xticks(rotation=0)
plt.show()