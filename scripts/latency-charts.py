#!/usr/bin/env python3
# pip install matplotlib numpy

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Constants: the nine “thread-operation” labels, and the DB ordering.
LABELS = [
    "1 Thread Sets", "1 Thread Gets", "1 Thread Totals",
    "2 Threads Sets", "2 Threads Gets", "2 Threads Totals",
    "8 Threads Sets", "8 Threads Gets", "8 Threads Totals"
]
DBS = ["Redis", "KeyDB", "Dragonfly", "Valkey"]


def parse_markdown(path):
    """
    Parse combined_all_results.md (or combined_all_results_tls.md) and return a nested dict:
      data[db]["avg"][label] = float(avg_latency)
      data[db]["p50"][label] = float(p50_latency)
      data[db]["p99"][label] = float(p99_latency)
    """
    data = {db: {"avg": {}, "p50": {}, "p99": {}} for db in DBS}

    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            # Skip blank lines, header rows (those starting with '|'), or pure '-----' lines
            if not line or line.startswith("|") or line.lower().startswith("databases") or set(line) <= set("- "):
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 8:
                continue  # malformed or not enough columns

            db_and_threads = parts[0]     # e.g. "Redis 1 Thread"
            op_type = parts[1]            # e.g. "Sets" / "Gets" / "Totals"
            # parts[5]: Avg latency, parts[6]: p50 latency, parts[7]: p99 latency
            avg_lat = parts[5]
            p50_lat = parts[6]
            p99_lat = parts[7]

            tokens = db_and_threads.split()
            if len(tokens) >= 3:
                db = tokens[0]
                threads = tokens[1] + " " + tokens[2]  # "1 Thread", "2 Threads", "8 Threads"
            else:
                continue

            label = f"{threads} {op_type}"
            if label not in LABELS or db not in data:
                continue

            try:
                avg_val = float(avg_lat)
                p50_val = float(p50_lat)
                p99_val = float(p99_lat)
            except ValueError:
                continue  # skip rows where latency isn’t a number

            data[db]["avg"][label] = avg_val
            data[db]["p50"][label] = p50_val
            data[db]["p99"][label] = p99_val

    return data


def plot_grouped_bars(all_data, metric_key, title_suffix, ylabel, out_filename):
    """
    Build a grouped‐bar chart from all_data[db][metric_key][label].
    Save to out_filename (PNG).
    """
    # Build a 2D array: each row = one DB, columns = each of the nine LABELS.
    vals = []
    for db in DBS:
        row = [all_data[db][metric_key].get(lab, 0.0) for lab in LABELS]
        vals.append(row)
    arr = np.array(vals)  # shape (4, 9)

    x = np.arange(len(LABELS))
    width = 0.2
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    fig, ax = plt.subplots(figsize=(14, 10))
    for i, db in enumerate(DBS):
        ax.bar(x + offsets[i], arr[i], width, label=db)

    ax.set_xticks(x)
    ax.set_xticklabels(LABELS, rotation=30, ha="right")
    ax.set_xlabel("Type of Operation and Threads")
    ax.set_ylabel(ylabel)
    ax.set_title(f"Redis vs KeyDB vs Dragonfly vs Valkey – {title_suffix}")
    ax.legend()

    # Annotate each bar with its numeric value
    for i, db in enumerate(DBS):
        for j, height in enumerate(arr[i]):
            ax.annotate(
                f"{height:.2f}",
                xy=(x[j] + offsets[i], height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom"
            )

    plt.tight_layout()
    plt.savefig(out_filename)
    plt.close()


if __name__ == "__main__":
    # Expect 2 arguments: 1) Markdown path, 2) prefix (e.g. "nonTLS" or "TLS")
    if len(sys.argv) < 3:
        print("Usage: python latency-charts.py <combined_md> <prefix>")
        sys.exit(1)

    md_path = sys.argv[1]
    prefix = sys.argv[2]

    # e.g. md_path="combined_all_results.md", prefix="nonTLS"
    data = parse_markdown(md_path)

    # Plot 3 separate charts, each saved under a distinct filename:
    plot_grouped_bars(
        data,
        "avg",
        "Average Latency (ms)",
        "Latency (ms)",
        f"latency-{prefix}-avg.png"
    )

    plot_grouped_bars(
        data,
        "p50",
        "p50 Latency (ms)",
        "Latency (ms)",
        f"latency-{prefix}-p50.png"
    )

    plot_grouped_bars(
        data,
        "p99",
        "p99 Latency (ms)",
        "Latency (ms)",
        f"latency-{prefix}-p99.png"
    )
