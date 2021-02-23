import os
import sys

import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import numpy as np



csv_name = sys.argv[1]
f = open(csv_name, 'r').read()

# TODO: parse the CSV in a way we can extract the time and queue_depth values for each switch

# TODO: set these properly according to the parsed data
x1 = x2 = x3 = x4 = []
y1 = y2 = y3 = y4 = []

# TODO: plot the queue depth values over time for each switch
plt.plot(x1, y1, 'o', color='red')
plt.plot(x2, y2, 'o', color='yellow')
plt.plot(x3, y3, 'o', color='green')
plt.plot(x4, y4, 'o', color='blue')
plt.show()
