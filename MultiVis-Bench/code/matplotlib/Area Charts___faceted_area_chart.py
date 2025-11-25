import matplotlib.pyplot as plt
import pandas as pd
from vega_datasets import data

source = data.stocks()
filtered_source = source[source['symbol'] != 'GOOG']

symbols = ["MSFT", "AAPL", "IBM", "AMZN"]

fig, axes = plt.subplots(len(symbols), 1, sharex=True)

for i, symbol in enumerate(symbols):
    ax = axes[i]
    symbol_data = filtered_source[filtered_source['symbol'] == symbol]

    ax.fill_between(symbol_data['date'], symbol_data['price'])

    if i < len(symbols) - 1:
        ax.set_xlabel('')
    else:
        ax.set_xlabel("Date")

    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    ax.set_ylim(bottom=0)

plt.show()