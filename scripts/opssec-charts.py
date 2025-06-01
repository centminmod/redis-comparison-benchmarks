#!/usr/bin/env python3
# pip install matplotlib numpy

import matplotlib.pyplot as plt
import numpy as np
import sys

# The nine “thread-operation” labels in exactly this order
EXPECTED_LABELS = [
    "1 Thread Sets", "1 Thread Gets", "1 Thread Totals",
    "2 Threads Sets", "2 Threads Gets", "2 Threads Totals",
    "8 Threads Sets", "8 Threads Gets", "8 Threads Totals"
]

# The four DBs we expect, in plotting order
DBS = ["Redis", "KeyDB", "Dragonfly", "Valkey"]


def normalize_threads(tokens):
    """
    Given tokens = e.g. ["Dragonfly", "1", "Threads"] or ["Dragonfly", "2", "Thread"],
    return (db, normalized_threads) as in latency-charts.py.
    """
    if len(tokens) < 2:
        return None, None

    db = tokens[0]
    num = tokens[1]
    thread_word = "Thread" if num == "1" else "Threads"
    normalized = f"{num} {thread_word}"
    return db, normalized


def parse_markdown_ops(filepath):
    """
    Read the combined_all_results.md (or combined_all_results_tls.md) table,
    return a dict of shape:
      data[db]["ops"] = { label: float }
    where label is one of EXPECTED_LABELS.
    """
    data = { db: {"ops": {lbl: 0.0 for lbl in EXPECTED_LABELS}} for db in DBS }

    print(f"[DEBUG] Opening file: {filepath}")
    with open(filepath, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            # Skip table headers or pure-separator lines:
            if line.startswith("|") or line.lower().startswith("databases") or set(line) <= set("- "):
                continue

            print(f"[DEBUG] Parsing line: “{line}”")
            parts = [p.strip() for p in line.split("|")]
            # We expect at least 3 columns (Databases/Threads, Type, Ops/sec, …).
            if len(parts) < 3:
                print(f"  [DEBUG] → Skipping because parts < 3: only {len(parts)} parts")
                continue

            db_and_threads = parts[0]   # e.g. "KeyDB 2 Threads" or "Dragonfly 1 Threads"
            op_type        = parts[1]   # "Sets", "Gets", or "Totals"
            ops_val        = parts[2]   # e.g. "54325.12"

            tokens = db_and_threads.split()
            db_name, threads_norm = normalize_threads(tokens)
            if db_name not in DBS or threads_norm is None:
                print(f"  [DEBUG] → Unknown DB or threading token: {tokens}")
                continue

            label = f"{threads_norm} {op_type}"
            if label not in EXPECTED_LABELS:
                print(f"  [DEBUG] → Label “{label}” not in EXPECTED_LABELS. Skipping.")
                continue

            try:
                opsf = float(ops_val)
            except ValueError:
                print(f"  [DEBUG] → Cannot convert Ops/sec to float: ops_val = {ops_val}")
                continue

            data[db_name]["ops"][label] = opsf
            print(f"  [DEBUG] → Stored {db_name}.{label} = {opsf:.2f} ops/sec")

    print("[DEBUG] Finished parsing file. Summary of ops/sec data:")
    for db in DBS:
        non_zero = {lbl: val for lbl, val in data[db]["ops"].items() if val != 0.0}
        print(f"  [DEBUG] DB = {db}: {len(non_zero)}/{len(EXPECTED_LABELS)} labels have non-zero ops/sec")
        for lbl, val in non_zero.items():
            print(f"    [DEBUG]   {lbl} → {val:.2f}")

    return data


def plot_ops_chart(all_data, out_filename):
    """
    Build a grouped‐bar chart of Ops/sec for the four DBS, each across the nine EXPECTED_LABELS.
    Save it to out_filename (PNG).
    """
    # Build a 2D array: each row = one DB, columns = each of the nine EXPECTED_LABELS
    vals = []
    for db in DBS:
        row = [ all_data[db]["ops"].get(lbl, 0.0) for lbl in EXPECTED_LABELS ]
        vals.append(row)
    arr = np.array(vals)  # shape (4, 9)

    x = np.arange(len(EXPECTED_LABELS))
    width = 0.2
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    fig, ax = plt.subplots(figsize=(14, 10))
    for i, db in enumerate(DBS):
        ax.bar(x + offsets[i], arr[i], width, label=db)

    ax.set_xticks(x)
    ax.set_xticklabels(EXPECTED_LABELS, rotation=30, ha="right")
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
    print(f"[DEBUG] Saving Ops/Sec plot to {out_filename}")
    plt.savefig(out_filename)
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python opssec-charts.py <combined_md> <prefix>")
        sys.exit(1)

    md_path = sys.argv[1]   # e.g. "combined_all_results.md"
    prefix  = sys.argv[2]   # e.g. "nonTLS" or "TLS"

    print(f"[DEBUG] Running opssec-charts.py on {md_path} with prefix “{prefix}”")
    data_ops = parse_markdown_ops(md_path)

    # Save to a single file, e.g. ops-nonTLS.png or ops-TLS.png
    plot_ops_chart(data_ops, f"ops-{prefix}.png")
