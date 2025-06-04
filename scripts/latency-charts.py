#!/usr/bin/env python3
# Requires: pip install matplotlib numpy

import argparse
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

# Exactly these four DB names in this plotting order:
DBS = ["Redis", "KeyDB", "Dragonfly", "Valkey"]


def normalize_threads(token):
    """
    Given a token like "1 Thread", "1 Threads", "2 Thread", "4 Threads", "8 Threads", etc.,
    return exactly "1 Thread", "2 Threads", "4 Threads", or "8 Threads", so that label = "<threads> <op>"
    matches one of EXPECTED_LABELS.
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


def parse_db_and_threads(db_and_threads):
    """
    Parse database name and thread info from strings like:
    - "Redis 1 Thread"
    - "Redis TLS 1 Thread" 
    - "Dragonfly 2 Thread"
    - "KeyDB TLS 4 Threads"
    
    Returns (db_name, thread_token) or (None, None) if parsing fails
    """
    tokens = db_and_threads.split()
    if len(tokens) < 3:
        return None, None
    
    # Handle TLS case: "Redis TLS 1 Thread" -> db="Redis", threads="1 Thread"
    if len(tokens) >= 4 and tokens[1] == "TLS":
        db = tokens[0]
        th_token = " ".join(tokens[2:4])  # "1 Thread"
        return db, th_token
    
    # Handle non-TLS case: "Redis 1 Thread" -> db="Redis", threads="1 Thread" 
    elif len(tokens) >= 3:
        db = tokens[0]
        th_token = " ".join(tokens[1:3])  # "1 Thread"
        return db, th_token
    
    return None, None


def parse_markdown(filepath):
    """
    Read combined_all_results.md (or combined_all_results_tls.md) line by line.
    Return a nested dict:
       data[db]["avg"][label], data[db]["p50"][label], data[db]["p99"][label]
    Initialized to 0.0 for every of the twelve EXPECTED_LABELS.
    Print debug lines for every skip/store.
    """
    data = {
        db: {
            "avg": {lbl: 0.0 for lbl in EXPECTED_LABELS},
            "p50": {lbl: 0.0 for lbl in EXPECTED_LABELS},
            "p99": {lbl: 0.0 for lbl in EXPECTED_LABELS}
        }
        for db in DBS
    }

    print(f"[DEBUG] Opening file: {filepath}")
    with open(filepath, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            # Skip markdown header separators and empty lines
            if not line or line.startswith("| ---") or "----" in line:
                continue

            if "|" not in line:
                print(f"  [DEBUG] Skipping: no '|' found -> {line}")
                continue

            parts = [p.strip() for p in line.split("|")]
            # Filter out empty parts
            parts = [p for p in parts if p]
            
            if len(parts) < 8:
                print(f"  [DEBUG] Skipping: fewer than 8 fields -> {parts}")
                continue

            db_and_threads = parts[0]  # e.g. "Redis 1 Thread" or "Redis TLS 1 Thread"
            op = parts[1]             # "Sets", "Gets", or "Totals"
            
            # Skip if this is a header row
            if op == "Type" or "Databases" in db_and_threads:
                continue
                
            try:
                avg_lat = parts[5]
                p50_lat = parts[6]
                p99_lat = parts[7]
            except IndexError:
                print(f"  [DEBUG] Skipping: missing latency columns -> {parts}")
                continue

            # Skip rows with "---" values
            if avg_lat == "---" or p50_lat == "---" or p99_lat == "---":
                print(f"  [DEBUG] Skipping: found '---' values in latency columns")
                continue

            db, th_token = parse_db_and_threads(db_and_threads)
            if db is None or th_token is None:
                print(f"  [DEBUG] SKIPPING: cannot parse db_and_threads '{db_and_threads}'")
                continue

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
                avg_val = float(avg_lat)
                p50_val = float(p50_lat)
                p99_val = float(p99_lat)
            except ValueError as e:
                print(f"  [DEBUG] SKIPPING: cannot convert latencies to float: avg={avg_lat}, p50={p50_lat}, p99={p99_lat}, error={e}")
                continue

            data[db]["avg"][label] = avg_val
            data[db]["p50"][label] = p50_val
            data[db]["p99"][label] = p99_val
            print(f"  [DEBUG] Stored -> {db}.{label} = avg {avg_val:.5f}, p50 {p50_val:.5f}, p99 {p99_val:.5f}")

    print("[DEBUG] Finished parsing. Summary of data loaded:")
    for db in DBS:
        print(f"  [DEBUG] DB = {db}")
        for metric in ["avg", "p50", "p99"]:
            nonzero = {lbl: val for lbl, val in data[db][metric].items() if val != 0.0}
            print(f"    [DEBUG]   {metric}: {len(nonzero)}/{len(EXPECTED_LABELS)} nonzero labels")
            if nonzero:
                for lbl, val in nonzero.items():
                    print(f"    [DEBUG]     {lbl} -> {val:.5f}")

    return data


def plot_grouped_bars(all_data, metric_key, title_suffix, ylabel, out_filename,
                        redis_io_threads, keydb_server_threads, dragonfly_proactor_threads, valkey_io_threads,
                        requests, clients, pipeline, data_size):
    """
    Build a grouped‐bar chart from all_data[db][metric_key][label]
    and save it to out_filename. Optimized for 12 data points:
    - Larger figure size for better spacing
    - Smaller font sizes for data labels
    - Rotated x-axis labels for better readability
    - Adjusted bar width and spacing
    """
    vals = []
    for db in DBS:
        row = [all_data[db][metric_key].get(lbl, 0.0) for lbl in EXPECTED_LABELS]
        vals.append(row)
    arr = np.array(vals)  # shape = (4, 12)

    x = np.arange(len(EXPECTED_LABELS))
    width = 0.18  # Reduced from 0.2 to give more space
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    # Increased figure size for better spacing with 12 data points
    fig, ax = plt.subplots(figsize=(20, 12))

    DBS_WITH_THREADS = [
        f"Redis io-threads {redis_io_threads}",
        f"KeyDB io-threads {keydb_server_threads}",
        f"Dragonfly proactor_threads {dragonfly_proactor_threads}",
        f"Valkey io-threads {valkey_io_threads}"
    ]

    for i, db_label in enumerate(DBS_WITH_THREADS):
        ax.bar(
            x + offsets[i],
            arr[i], # arr is ordered by DBS, not DBS_WITH_THREADS
            width,
            label=db_label
        )

    title_parts = [
        "Redis vs KeyDB vs Dragonfly vs Valkey – Memtier Benchmarks (4 vCPU VM)",
        f"(requests:{requests} clients:{clients} pipeline:{pipeline} data_size:{data_size})",
        "(lower is better) by George Liu"
    ]
    ax.set_title(
        "\n".join(title_parts),
        fontsize=18,
        fontweight='bold',
        loc='center'
    )
    ax.set_ylabel(ylabel, fontsize=14, fontweight='semibold')
    ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_xticks(x)
    # Rotate x-axis labels for better readability with 12 labels
    ax.set_xticklabels(EXPECTED_LABELS, rotation=45, ha="right", fontsize=9)
    
    # Position legend outside the plot area to avoid masking data
    ax.legend(fontsize=9.5, bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    
    ax.tick_params(axis='y', labelsize=12)

    # Only add annotations for non-zero values
    for i, db in enumerate(DBS):
        for j, height in enumerate(arr[i]):
            if height > 0:  # Only annotate non-zero bars
                ax.annotate(
                    f"{height:.2f}",
                    xy=(x[j] + offsets[i], height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=7  # Reduced from 9 to 7
                )

    plt.tight_layout(rect=[0, 0, 0.85, 0.94])  # Adjusted to leave space for external legend
    print(f"[DEBUG] Saving plot to {out_filename}")
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')  # Higher DPI for better quality
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate latency charts from benchmark data.")
    parser.add_argument("md_path", help="Path to the markdown file with benchmark results (e.g., combined_all_results.md)")
    parser.add_argument("prefix", help="Prefix for output file names (e.g., nonTLS or TLS)")
    parser.add_argument("--redis_io_threads", default='2', help="Redis IO threads")
    parser.add_argument("--keydb_server_threads", default='2', help="KeyDB server threads")
    parser.add_argument("--dragonfly_proactor_threads", default='3', help="Dragonfly proactor threads")
    parser.add_argument("--valkey_io_threads", default='1', help="Valkey IO threads")
    parser.add_argument("--requests", default='2000', help="Number of requests")
    parser.add_argument("--clients", default='100', help="Number of clients")
    parser.add_argument("--pipeline", default='1', help="Pipeline depth")
    parser.add_argument("--data_size", default='1024', help="Data size in bytes")

    args = parser.parse_args()

    print(f"[DEBUG] Running latency-charts.py on '{args.md_path}' with prefix '{args.prefix}'")
    data = parse_markdown(args.md_path)

    plot_grouped_bars(
        data,
        "avg",
        "Average Latency (ms)",
        "Latency (ms)",
        f"latency-{args.prefix}-avg.png",
        args.redis_io_threads,
        args.keydb_server_threads,
        args.dragonfly_proactor_threads,
        args.valkey_io_threads,
        args.requests,
        args.clients,
        args.pipeline,
        args.data_size
    )
    plot_grouped_bars(
        data,
        "p50",
        "p50 Latency (ms)",
        "Latency (ms)",
        f"latency-{args.prefix}-p50.png",
        args.redis_io_threads,
        args.keydb_server_threads,
        args.dragonfly_proactor_threads,
        args.valkey_io_threads,
        args.requests,
        args.clients,
        args.pipeline,
        args.data_size
    )
    plot_grouped_bars(
        data,
        "p99",
        "p99 Latency (ms)",
        "Latency (ms)",
        f"latency-{args.prefix}-p99.png",
        args.redis_io_threads,
        args.keydb_server_threads,
        args.dragonfly_proactor_threads,
        args.valkey_io_threads,
        args.requests,
        args.clients,
        args.pipeline,
        args.data_size
    )