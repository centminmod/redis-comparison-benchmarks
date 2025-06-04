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


def plot_latency_chart_single(all_data, metric_key, title_suffix, ylabel, out_filename, redis_io_threads, keydb_server_threads, dragonfly_proactor_threads, valkey_io_threads, requests, clients, pipeline, data_size):
    """Build single grouped-bar chart with improved spacing and fonts"""
    print(f"[DEBUG] Starting single chart generation: {out_filename}")
    
    vals = []
    for db in DBS:
        row = [all_data[db][metric_key].get(lbl, 0.0) for lbl in EXPECTED_LABELS]
        vals.append(row)
    arr = np.array(vals)

    x = np.arange(len(EXPECTED_LABELS))
    width = 0.15
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    fig, ax = plt.subplots(figsize=(24, 10))

    DBS_WITH_THREADS = [f"Redis io-threads {redis_io_threads}", f"KeyDB io-threads {keydb_server_threads}", f"Dragonfly proactor_threads {dragonfly_proactor_threads}", f"Valkey io-threads {valkey_io_threads}"]

    for i, db_label in enumerate(DBS_WITH_THREADS):
        ax.bar(x + offsets[i], arr[i], width, label=db_label)

    title_parts = ["Redis vs KeyDB vs Dragonfly vs Valkey – Memtier Benchmarks (4 vCPU VM)", f"(requests:{requests} clients:{clients} pipeline:{pipeline} data_size:{data_size})", "(lower is better) by George Liu"]
    ax.set_title("\n".join(title_parts), fontsize=20, fontweight='bold', pad=20)
    ax.set_ylabel(ylabel, fontsize=16, fontweight='semibold')
    ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(EXPECTED_LABELS, rotation=35, ha="right", fontsize=11)
    ax.legend(fontsize=12, bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.tick_params(axis='y', labelsize=13)

    for i, db in enumerate(DBS):
        for j, height in enumerate(arr[i]):
            if height > 0:
                ax.annotate(f"{height:.2f}", xy=(x[j] + offsets[i], height), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    print(f"[DEBUG] Saving plot to {out_filename}")
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[DEBUG] Successfully saved {out_filename}")


def plot_latency_chart_grid(all_data, metric_key, title_suffix, ylabel, out_filename, redis_io_threads, keydb_server_threads, dragonfly_proactor_threads, valkey_io_threads, requests, clients, pipeline, data_size):
    """Build 2x2 subplot grid - one subplot per thread count"""
    print(f"[DEBUG] Starting grid chart generation: {out_filename}")
    
    thread_counts = ["1 Thread", "2 Threads", "4 Threads", "8 Threads"]
    operations = ["Sets", "Gets", "Totals"]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    DBS_WITH_THREADS = [f"Redis io-threads {redis_io_threads}", f"KeyDB io-threads {keydb_server_threads}", f"Dragonfly proactor_threads {dragonfly_proactor_threads}", f"Valkey io-threads {valkey_io_threads}"]
    
    colors = plt.cm.Set1(np.linspace(0, 1, len(DBS)))
    
    for idx, thread_count in enumerate(thread_counts):
        ax = axes[idx]
        x = np.arange(len(operations))
        width = 0.2
        offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]
        
        for i, db in enumerate(DBS):
            values = []
            for op in operations:
                label = f"{thread_count} {op}"
                values.append(all_data[db][metric_key].get(label, 0.0))
            
            bars = ax.bar(x + offsets[i], values, width, label=DBS_WITH_THREADS[i], color=colors[i])
            
            for j, height in enumerate(values):
                if height > 0:
                    ax.annotate(f"{height:.2f}", xy=(x[j] + offsets[i], height), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
        
        ax.set_title(f"{thread_count}", fontsize=14, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(operations, fontsize=11)
        ax.grid(axis='y', linestyle='--', linewidth=0.3, alpha=0.7)
        ax.tick_params(axis='y', labelsize=10)

    title_parts = ["Redis vs KeyDB vs Dragonfly vs Valkey – Memtier Benchmarks (4 vCPU VM)", f"(requests:{requests} clients:{clients} pipeline:{pipeline} data_size:{data_size})", "(lower is better) by George Liu"]
    fig.suptitle("\n".join(title_parts), fontsize=16, fontweight='bold', y=0.98)
    
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=11)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.15)
    print(f"[DEBUG] Saving plot to {out_filename}")
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[DEBUG] Successfully saved {out_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate latency charts from benchmark data.")
    parser.add_argument("md_path", help="Path to the markdown file with benchmark results")
    parser.add_argument("prefix", help="Prefix for output file names")
    parser.add_argument("--layout", choices=["single", "grid"], default="single", help="Chart layout: single (default) or grid (2x2 subplots)")
    parser.add_argument("--redis_io_threads", default='2', help="Redis IO threads")
    parser.add_argument("--keydb_server_threads", default='2', help="KeyDB server threads")
    parser.add_argument("--dragonfly_proactor_threads", default='3', help="Dragonfly proactor threads")
    parser.add_argument("--valkey_io_threads", default='1', help="Valkey IO threads")
    parser.add_argument("--requests", default='2000', help="Number of requests")
    parser.add_argument("--clients", default='100', help="Number of clients")
    parser.add_argument("--pipeline", default='1', help="Pipeline depth")
    parser.add_argument("--data_size", default='1024', help="Data size in bytes")

    args = parser.parse_args()

    print(f"[DEBUG] Running latency-charts.py with layout='{args.layout}'")
    data = parse_markdown(args.md_path)

    for metric_key, ylabel in [("avg", "Average Latency (ms)"), ("p50", "p50 Latency (ms)"), ("p99", "p99 Latency (ms)")]:
        out_filename = f"latency-{args.prefix}-{metric_key}-{args.layout}.png"
        print(f"[DEBUG] Output filename will be: {out_filename}")
        
        if args.layout == "grid":
            plot_latency_chart_grid(data, metric_key, ylabel, ylabel, out_filename, args.redis_io_threads, args.keydb_server_threads, args.dragonfly_proactor_threads, args.valkey_io_threads, args.requests, args.clients, args.pipeline, args.data_size)
        else:
            plot_latency_chart_single(data, metric_key, ylabel, ylabel, out_filename, args.redis_io_threads, args.keydb_server_threads, args.dragonfly_proactor_threads, args.valkey_io_threads, args.requests, args.clients, args.pipeline, args.data_size)
    
    print("[DEBUG] Script completed")