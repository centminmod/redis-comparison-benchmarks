#!/usr/bin/env python3
# Requires: pip install matplotlib numpy

import matplotlib.pyplot as plt
import numpy as np
import sys

# Updated to include 4 threads
EXPECTED_LABELS = [
    "1 Thread Sets", "1 Thread Gets", "1 Thread Totals",
    "2 Threads Sets", "2 Threads Gets", "2 Threads Totals",
    "4 Threads Sets", "4 Threads Gets", "4 Threads Totals",
    "8 Threads Sets", "8 Threads Gets", "8 Threads Totals"
]

# The four DBs we care about, in plotting order:
DBS = ["Redis", "KeyDB", "Dragonfly", "Valkey"]


def normalize_threads(token):
    """
    Given "1 Thread", "1 Threads", "2 Thread", "4 Threads", "8 Threads", etc.,
    return exactly "1 Thread", "2 Threads", "4 Threads", or "8 Threads".
    """
    parts = token.split()
    if len(parts) != 2:
        return None
    num, word = parts
    if num == "1":
        return "1 Thread"
    elif num in ("2", "4", "8"):
        return f"{num} Threads"
    else:
        return None


def parse_markdown_ops(filepath):
    """
    Read combined_all_results.md (or combined_all_results_tls.md). Return:
      data[db]["ops"][label] = float(ops/sec)
    Prints debug lines for every skipped row or stored value.
    """
    data = {
        db: {"ops": {lbl: 0.0 for lbl in EXPECTED_LABELS}}
        for db in DBS
    }

    print(f"[DEBUG] Opening file: {filepath}")
    with open(filepath, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            if "|" not in line:
                print(f"  [DEBUG] Skipping: no '|' found → "{line}"")
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5:
                print(f"  [DEBUG] Skipping: fewer than 5 fields → {parts}")
                continue

            db_and_threads = parts[0]
            op = parts[1]
            try:
                ops_val = parts[2]
            except IndexError:
                print(f"  [DEBUG] Skipping: missing Ops/sec column, parts = {parts}")
                continue

            tokens = db_and_threads.split()
            if len(tokens) < 3:
                print(f"  [DEBUG] SKIPPING: cannot split db_and_threads '{db_and_threads}'")
                continue

            db = tokens[0]
            th_token = " ".join(tokens[1:3])

            if db not in DBS:
                print(f"  [DEBUG] SKIPPING: Unknown DB '{db}'")
                continue

            th_norm = normalize_threads(th_token)
            if th_norm is None:
                print(f"  [DEBUG] SKIPPING: cannot normalize threads '{th_token}'")
                continue

            label = f"{th_norm} {op}"
            if label not in EXPECTED_LABELS:
                print(f"  [DEBUG] SKIPPING: label '{label}' not in EXPECTED_LABELS")
                continue

            try:
                opsf = float(ops_val)
            except ValueError:
                print(f"  [DEBUG] SKIPPING: cannot convert Ops/sec to float: '{ops_val}'")
                continue

            data[db]["ops"][label] = opsf
            print(f"  [DEBUG] Stored → {db}.{label} = {opsf:.2f} ops/sec")

    print("[DEBUG] Finished parsing. Summary of ops/sec data:")
    for db in DBS:
        nonzero = {lbl: val for lbl, val in data[db]["ops"].items() if val != 0.0}
        print(f"  [DEBUG] DB = {db}: {len(nonzero)}/{len(EXPECTED_LABELS)} nonzero labels")
        if nonzero:
            for lbl, val in nonzero.items():
                print(f"    [DEBUG]   {lbl} → {val:.2f}")

    return data


def plot_ops_chart(all_data, out_filename):
    """
    Build a grouped‐bar chart for Ops/sec across 4 DBs and 12 labels,
    and save to out_filename. Optimized for 12 data points:
    - Larger figure size for better spacing
    - Smaller font sizes for data labels
    - Rotated x-axis labels for better readability
    - Adjusted bar width and spacing
    """
    vals = []
    for db in DBS:
        row = [all_data[db]["ops"].get(lbl, 0.0) for lbl in EXPECTED_LABELS]
        vals.append(row)
    arr = np.array(vals)  # shape = (4, 12)

    x = np.arange(len(EXPECTED_LABELS))
    width = 0.18  # Reduced from 0.2 to give more space
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    # Increased figure size for better spacing with 12 data points
    fig, ax = plt.subplots(figsize=(20, 12))
    for i, db in enumerate(DBS):
        ax.bar(
            x + offsets[i],
            arr[i],
            width,
            label=db
        )

    ax.set_title(
        "Redis vs KeyDB vs Dragonfly vs Valkey – Memtier Benchmarks (4 vCPU VM)\nby George Liu",
        fontsize=18,
        fontweight='bold',
        loc='center'
    )
    ax.set_ylabel("Ops/Sec", fontsize=14, fontweight='semibold')
    ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_xticks(x)
    # Rotate x-axis labels for better readability with 12 labels
    ax.set_xticklabels(EXPECTED_LABELS, rotation=45, ha="right", fontsize=9)
    ax.legend(fontsize=12, loc='upper left')
    ax.tick_params(axis='y', labelsize=12)

    # Smaller font size for data value annotations
    for i, db in enumerate(DBS):
        for j, height in enumerate(arr[i]):
            ax.annotate(
                f"{int(round(height))}",
                xy=(x[j] + offsets[i], height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=7  # Reduced from 9 to 7
            )

    plt.tight_layout(rect=[0, 0, 1, 0.94])  # Adjusted for rotated labels
    print(f"[DEBUG] Saving Ops/Sec plot to {out_filename}")
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')  # Higher DPI for better quality
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python opssec-charts.py <combined_md> <prefix>")
        sys.exit(1)

    md_path = sys.argv[1]  # e.g. "combined_all_results.md"
    prefix = sys.argv[2]   # e.g. "nonTLS" or "TLS"

    print(f"[DEBUG] Running opssec-charts.py on '{md_path}' with prefix '{prefix}'")
    data_ops = parse_markdown_ops(md_path)

    plot_ops_chart(data_ops, f"ops-{prefix}.png")