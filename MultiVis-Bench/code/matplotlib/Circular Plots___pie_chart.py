import matplotlib.pyplot as plt

categories = [1, 2, 3, 4, 5, 6]
values = [4, 6, 10, 3, 7, 8]

fig, ax = plt.subplots()
wedges, texts = ax.pie(values, startangle=90, counterclock=False)
ax.legend(wedges, categories)
ax.axis('equal')

plt.show()