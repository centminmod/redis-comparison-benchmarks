#!/usr/bin/env python3
# pip install matplotlib numpy
import matplotlib.pyplot as plt
import numpy as np

# Data for x-axis labels and bar width
labels = ['1 Thread Sets', '1 Thread Gets', '1 Thread Totals', '2 Threads Sets', '2 Threads Gets', '2 Threads Totals', '8 Threads Sets', '8 Threads Gets', '8 Threads Totals']
width = 0.2
x = np.arange(len(labels))  # Defining x variable

# Updated Data for latencies
avg_latency_data = [
    [1.68332, 1.63532, 1.63832, 3.25753, 3.08650, 3.09719, 9.20864, 9.09222, 9.09950], # Redis
    [1.14006, 1.08299, 1.08656, 1.38931, 1.31553, 1.32014, 5.38483, 5.31853, 5.32267], # KeyDB
    [1.36691, 1.30565, 1.30948, 1.52514, 1.50333, 1.50470, 2.48188, 2.44320, 2.44562]  # Dragonfly
]

p50_latency_data = [
    [1.439, 1.415, 1.415, 1.463, 1.455, 1.455, 9.855, 9.727, 9.727], # Redis
    [1.007, 1.007, 1.007, 1.295, 1.287, 1.287, 0.887, 0.879, 0.879], # KeyDB
    [0.959, 0.967, 0.967, 0.743, 0.743, 0.743, 1.767, 1.735, 1.735]  # Dragonfly
]

p99_latency_data = [
    [9.855, 3.247, 3.263, 18.559, 15.743, 15.935, 29.695, 28.927, 29.055], # Redis
    [3.327, 1.831, 1.839, 2.191, 2.079, 2.079, 98.303, 97.791, 97.791], # KeyDB
    [9.087, 8.767, 8.767, 12.735, 12.607, 12.607, 11.007, 10.431, 10.495]  # Dragonfly
]

def plot_latency_chart(data, title):
    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot data
    rects1 = ax.bar(x - width, data[0], width, label='Redis', color='blue')
    rects2 = ax.bar(x, data[1], width, label='KeyDB', color='green')
    rects3 = ax.bar(x + width, data[2], width, label='Dragonfly', color='red')

    # Labels, title and ticks
    ax.set_xlabel('Type of Operation and Threads')
    ax.set_ylabel('Latency (ms)')
    ax.set_title(f'Redis vs KeyDB vs Dragonfly {title}\nby George Liu')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # Attach data labels
    def attach_vertical_data_labels(rects):
        """Attach a text label above each bar in *rects*, displaying its height, rounded to 2 decimal places."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(round(height, 2)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    attach_vertical_data_labels(rects1)
    attach_vertical_data_labels(rects2)
    attach_vertical_data_labels(rects3)

    plt.tight_layout()
    plt.show()

# Plotting the 3 charts
plot_latency_chart(avg_latency_data, 'Average Latency (ms)')
plot_latency_chart(p50_latency_data, 'p50 Latency (ms)')
plot_latency_chart(p99_latency_data, 'p99 Latency (ms)')