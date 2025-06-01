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
    force them into either "1 Thread" or "2 Threads" or "8 Threads" depending on the number.
    """
    if len(tokens) < 2:
        return None, None

    db = tokens[0]
    num = tokens[1]
    # Always singular “Thread” when num == "1", else plural “Threads”
    thread_word = "Thread" if num == "1" else "Threads"
    normalized = f"{num} {thread_word}"
    return db, normalized


def parse_markdown(filepath):
    """
    Read the combined_all_results.md (or combined_all_results_tls.md) table,
    return a dict of shape:
      data = {
        "Redis":   {"avg": {label: float}, "p50": {...},  "p99": {...}},
        "KeyDB":   { ... },
        "Dragonfly": { ... },
        "Valkey": { ... }
      }
    Any row that cannot be parsed exactly into one of the nine EXPECTED_LABELS
    for one of the four DBS will be skipped—but we print debug lines so you can see why.
    """
    # Initialize empty structures
    data = {
        db: {
            "avg":   { lbl: 0.0 for lbl in EXPECTED_LABELS },
            "p50":   { lbl: 0.0 for lbl in EXPECTED_LABELS },
            "p99":   { lbl: 0.0 for lbl in EXPECTED_LABELS }
        }
        for db in DBS
    }

    print(f"[DEBUG] Opening file: {filepath}")
    with open(filepath, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            # Skip table headers or pure-separator lines:
            #   - Any line that begins with '|' is a Markdown header or separator
            #   - Any line whose characters are only '-' or ' ' is a bare separator
            #   - Any line that starts with “Databases” (case-insensitive)
            if line.startswith("|") or line.lower().startswith("databases") or set(line) <= set("- "):
                continue

            print(f"[DEBUG] Parsing line: “{line}”")
            parts = [p.strip() for p in line.split("|")]
            # We expect at least 9 columns (Databases/Threads, Type, Ops/sec, Hits/sec, Misses/sec,
            # Avg Latency, p50 Latency, p99 Latency, p99.9 Latency, KB/sec).
            if len(parts) < 8:
                print(f"  [DEBUG] → Skipping because parts < 8: {len(parts)} parts")
                continue

            db_and_threads = parts[0]   # e.g. "Redis 1 Thread" or "Dragonfly 1 Threads"
            op_type        = parts[1]   # e.g. "Sets", "Gets", or "Totals"

            # The six fields we care about:
            #  parts[5] = Avg Latency, parts[6] = p50 Latency, parts[7] = p99 Latency
            avg_lat = parts[5]
            p50_lat = parts[6]
            p99_lat = parts[7]

            # Normalize the DB name and "threads" wording
            tokens = db_and_threads.split()
            db_name, threads_norm = normalize_threads(tokens)
            if db_name not in DBS or threads_norm is None:
                print(f"  [DEBUG] → Unknown DB or threading token: tokens={tokens}")
                continue

            # Reconstruct the label exactly as one of EXPECTED_LABELS
            label = f"{threads_norm} {op_type}"
            if label not in EXPECTED_LABELS:
                print(f"  [DEBUG] → Label “{label}” not in EXPECTED_LABELS. Skipping.")
                continue

            try:
                avg_val = float(avg_lat)
                p50_val = float(p50_lat)
                p99_val = float(p99_lat)
            except ValueError:
                print(f"  [DEBUG] → Cannot convert latencies to float: avg={avg_lat}, p50={p50_lat}, p99={p99_lat}")
                continue

            # Store into our dict
            data[db_name]["avg"][label] = avg_val
            data[db_name]["p50"][label] = p50_val
            data[db_name]["p99"][label] = p99_val
            print(f"  [DEBUG] → Stored {db_name}.{label} → avg={avg_val}, p50={p50_val}, p99={p99_val}")

    print("[DEBUG] Finished parsing file. Summary of data loaded:")
    for db in DBS:
        print(f"  [DEBUG] DB = {db}")
        for metric in ["avg", "p50", "p99"]:
            non_zero = {lbl: val for lbl, val in data[db][metric].items() if val != 0.0}
            print(f"    [DEBUG]   {metric}: {len(non_zero)}/{len(EXPECTED_LABELS)} labels have values")
            # Print them out if you want
            for lbl, val in non_zero.items():
                print(f"    [DEBUG]     {lbl} → {val:.5f}")

    return data


def plot_grouped_bars(all_data, metric_key, title_suffix, ylabel, out_filename):
    """
    Build a grouped‐bar chart from all_data[db][metric_key][label].
    Save it to out_filename (PNG).
    """
    # Build a 2D array: each row = one DB, columns = each of the nine EXPECTED_LABELS
    vals = []
    for db in DBS:
        row = [ all_data[db][metric_key].get(lbl, 0.0) for lbl in EXPECTED_LABELS ]
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
    print(f"[DEBUG] Saving plot to {out_filename}")
    plt.savefig(out_filename)
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python latency-charts.py <combined_md> <prefix>")
        sys.exit(1)

    md_path = sys.argv[1]       # e.g. "combined_all_results.md"
    prefix  = sys.argv[2]       # e.g. "nonTLS" or "TLS"

    print(f"[DEBUG] Running latency-charts.py on {md_path} with prefix “{prefix}”")
    data = parse_markdown(md_path)

    # Generate three separate PNG files (avg, p50, p99) with distinct names
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
