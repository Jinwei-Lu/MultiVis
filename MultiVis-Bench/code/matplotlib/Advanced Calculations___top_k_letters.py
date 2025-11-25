import matplotlib.pyplot as plt
import pandas as pd

text = """
It was the best of times, it was the worst of times, it was the age of wisdom,
it was the age of foolishness, it was the epoch of belief, it was the epoch of
incredulity, it was the season of Light, it was the season of Darkness, it was
the spring of hope, it was the winter of despair, we had everything before us,
we had nothing before us, we were all going direct to Heaven, we were all going
direct the other way - in short, the period was so far like the present period,
that some of its noisiest authorities insisted on its being received, for good
or for evil, in the superlative degree of comparison only.
"""

source = pd.DataFrame(
    {'letters': [c.lower() for c in text if c.isalpha()]}
)

letter_counts = source['letters'].value_counts().reset_index()
letter_counts.columns = ['letters', 'count']

letter_counts = letter_counts.sort_values('count', ascending=False).head(10)

plt.bar(letter_counts['letters'], letter_counts['count'])
plt.xlabel('Count')
plt.ylabel('Letters')
plt.gca().invert_xaxis()
plt.show()