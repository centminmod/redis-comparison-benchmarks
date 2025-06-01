#!/usr/bin/env python3
# pip install matplotlib numpy

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Constants: nine “thread-operation” labels and DB ordering.
LABELS = [
    "1 Thread Sets", "1 Thread Gets", "1 Thread Totals",
    "2 Threads Sets", "2 Threads Gets", "2 Threads Totals",
    "8 Threads Sets", "8 Threads Gets", "8 Threads Totals"
]
DBS = ["Redis", "KeyDB", "Dragonfly", "Valkey"]


def parse_markdown_ops(path):
    """
    Parse combined_all_results.md (or combined_all_results_tls.md) and return:
      data[db]["ops"][label] = float(ops/sec)
    """
    data = {db: {"ops": {}} for db in DBS}

    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            # Skip blank lines or header/separator rows
            if not line or line.startswith("|") or line.lower().startswith("databases") or set(line) <= set("- "):
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                continue

            db_and_threads = parts[0]   # e.g. "Redis 1 Thread"
            op_type = parts[1]          # e.g. "Sets"/"Gets"/"Totals"
            ops_val = parts[2]          # e.g. "86284.73"

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
                opsf = float(ops_val)
            except ValueError:
                continue

            data[db]["ops"][label] = opsf

    return data


def plot_ops_chart(all_data, out_filename):
    """
    Plot a grouped bar chart of Ops/sec for Redis, KeyDB, Dragonfly, Valkey.
    Save it to out_filename (PNG).
    """
    # Build array shape (4, 9)
    vals = []
    for db in DBS:
        row = [all_data[db]["ops"].get(lab, 0.0) for lab in LABELS]
        vals.append(row)
    arr = np.array(vals)

    x = np.arange(len(LABELS))
    width = 0.2
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    fig, ax = plt.subplots(figsize=(14, 10))
    for i, db in enumerate(DBS):
        ax.bar(x + offsets[i], arr[i], width, label=db)

    ax.set_xticks(x)
    ax.set_xticklabels(LABELS, rotation=30, ha="right")
    ax.set_xlabel("Type of Operation and Threads")
    ax.set_ylabel("Ops/Sec")
    ax.set_title("Redis vs KeyDB vs Dragonfly vs Valkey – Ops/Sec")
    ax.legend()

    for i, db in enumerate(DBS):
        for j, height in enumerate(arr[i]):
            ax.annotate(
                f"{int(round(height))}",
                xy=(x[j] + offsets[i], height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom"
            )

    plt.tight_layout()
    plt.savefig(out_filename)
    plt.close()


if __name__ == "__main__":
    # Expect 2 arguments: Markdown path, and prefix (e.g. “nonTLS” or “TLS”)
    if len(sys.argv) < 3:
        print("Usage: python opssec-charts.py <combined_md> <prefix>")
        sys.exit(1)

    md_path = sys.argv[1]
    prefix = sys.argv[2]

    data_ops = parse_markdown_ops(md_path)
    plot_ops_chart(data_ops, f"ops-{prefix}.png")
