#!/usr/bin/env python3
# pip install matplotlib numpy
import numpy as np
import matplotlib.pyplot as plt

# Data
labels = ['1 Thread Sets', '1 Thread Gets', '1 Thread Totals', '2 Threads Sets', '2 Threads Gets', '2 Threads Totals', '8 Threads Sets', '8 Threads Gets', '8 Threads Totals']

ops_sec_data = [
    [3814.44, 57216.58, 61031.02, 3927.15, 58907.31, 62834.47, 5961.01, 89415.13, 95376.14], # Redis
    [5752.32, 86284.73, 92037.05, 9541.41, 143121.19, 152662.61, 11152.45, 167286.71, 178439.15], # KeyDB
    [6379.52, 95692.75, 102072.27, 8296.79, 124451.91, 132748.71, 21324.85, 319872.80, 341197.65] # Dragonfly
]

# Update chart title

fig, ax = plt.subplots(figsize=(14, 10))

# Plot data
width = 0.2
x = np.arange(len(labels))
rects1 = ax.bar(x - width, ops_sec_data[0], width, label='Redis', color='blue')
rects2 = ax.bar(x, ops_sec_data[1], width, label='KeyDB', color='green')
rects3 = ax.bar(x + width, ops_sec_data[2], width, label='Dragonfly', color='red')

# Add some text for labels, title, and custom x-axis tick labels, etc.
ax.set_xlabel('Type of Operation and Threads')
ax.set_ylabel('Ops/Sec')
ax.set_title('Redis vs KeyDB vs Dragonfly Memtier Benchmarks\nby George Liu')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Attach data labels
def attach_data_labels(rects):
    """Attach a text label above each bar in *rects*, displaying its height, rounded to 0 decimal places."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(int(round(height))),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

attach_data_labels(rects1)
attach_data_labels(rects2)
attach_data_labels(rects3)

plt.tight_layout()
plt.show()