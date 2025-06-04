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

            # Skip markdown header separators and empty lines
            if not line or line.startswith("| ---") or "----" in line:
                continue

            if "|" not in line:
                print(f"  [DEBUG] Skipping: no '|' found -> {line}")
                continue

            parts = [p.strip() for p in line.split("|")]
            # Filter out empty parts
            parts = [p for p in parts if p]
            
            if len(parts) < 5:
                print(f"  [DEBUG] Skipping: fewer than 5 fields -> {parts}")
                continue

            db_and_threads = parts[0]
            op = parts[1]
            
            # Skip if this is a header row
            if op == "Type" or "Databases" in db_and_threads:
                continue
                
            try:
                ops_val = parts[2]
            except IndexError:
                print(f"  [DEBUG] Skipping: missing Ops/sec column, parts = {parts}")
                continue

            # Skip rows with "---" values
            if ops_val == "---":
                print(f"  [DEBUG] Skipping: found '---' value in ops/sec column")
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
                opsf = float(ops_val)
            except ValueError as e:
                print(f"  [DEBUG] SKIPPING: cannot convert Ops/sec to float: '{ops_val}', error={e}")
                continue

            data[db]["ops"][label] = opsf
            print(f"  [DEBUG] Stored -> {db}.{label} = {opsf:.2f} ops/sec")

    print("[DEBUG] Finished parsing. Summary of ops/sec data:")
    for db in DBS:
        nonzero = {lbl: val for lbl, val in data[db]["ops"].items() if val != 0.0}
        print(f"  [DEBUG] DB = {db}: {len(nonzero)}/{len(EXPECTED_LABELS)} nonzero labels")
        if nonzero:
            for lbl, val in nonzero.items():
                print(f"    [DEBUG]   {lbl} -> {val:.2f}")

    return data


def plot_ops_chart_single(all_data, out_filename, redis_io_threads, keydb_server_threads, dragonfly_proactor_threads, valkey_io_threads, requests, clients, pipeline, data_size):
    """Build single grouped-bar chart with improved spacing and fonts"""
    vals = []
    for db in DBS:
        row = [all_data[db]["ops"].get(lbl, 0.0) for lbl in EXPECTED_LABELS]
        vals.append(row)
    arr = np.array(vals)

    x = np.arange(len(EXPECTED_LABELS))
    width = 0.15
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    fig, ax = plt.subplots(figsize=(24, 10))

    DBS_WITH_THREADS = [f"Redis io-threads {redis_io_threads}", f"KeyDB io-threads {keydb_server_threads}", f"Dragonfly proactor_threads {dragonfly_proactor_threads}", f"Valkey io-threads {valkey_io_threads}"]

    for i, db_label in enumerate(DBS_WITH_THREADS):
        ax.bar(x + offsets[i], arr[i], width, label=db_label)

    title_parts = ["Redis vs KeyDB vs Dragonfly vs Valkey – Memtier Benchmarks (4 vCPU VM)", f"(requests:{requests} clients:{clients} pipeline:{pipeline} data_size:{data_size})", "(higher is better) by George Liu"]
    ax.set_title("\n".join(title_parts), fontsize=20, fontweight='bold', pad=20)
    ax.set_ylabel("Ops/Sec", fontsize=16, fontweight='semibold')
    ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(EXPECTED_LABELS, rotation=35, ha="right", fontsize=11)
    ax.legend(fontsize=12, bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.tick_params(axis='y', labelsize=13)

    for i, db in enumerate(DBS):
        for j, height in enumerate(arr[i]):
            if height > 0:
                ax.annotate(f"{int(round(height))}", xy=(x[j] + offsets[i], height), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close()


def plot_ops_chart_grid(all_data, out_filename, redis_io_threads, keydb_server_threads, dragonfly_proactor_threads, valkey_io_threads, requests, clients, pipeline, data_size):
    """Build 2x2 subplot grid - one subplot per thread count"""
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
                values.append(all_data[db]["ops"].get(label, 0.0))
            
            bars = ax.bar(x + offsets[i], values, width, label=DBS_WITH_THREADS[i], color=colors[i])
            
            for j, height in enumerate(values):
                if height > 0:
                    ax.annotate(f"{int(round(height))}", xy=(x[j] + offsets[i], height), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
        
        ax.set_title(f"{thread_count}", fontsize=14, fontweight='bold')
        ax.set_ylabel("Ops/Sec", fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(operations, fontsize=11)
        ax.grid(axis='y', linestyle='--', linewidth=0.3, alpha=0.7)
        ax.tick_params(axis='y', labelsize=10)

    title_parts = ["Redis vs KeyDB vs Dragonfly vs Valkey – Memtier Benchmarks (4 vCPU VM)", f"(requests:{requests} clients:{clients} pipeline:{pipeline} data_size:{data_size})", "(higher is better) by George Liu"]
    fig.suptitle("\n".join(title_parts), fontsize=16, fontweight='bold', y=0.98)
    
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=11)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.15)
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Ops/sec charts from benchmark data.")
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

    print(f"[DEBUG] Running opssec-charts.py with layout='{args.layout}'")
    data_ops = parse_markdown_ops(args.md_path)

    out_filename = f"ops-{args.prefix}-{args.layout}.png"
    
    if args.layout == "grid":
        plot_ops_chart_grid(data_ops, out_filename, args.redis_io_threads, args.keydb_server_threads, args.dragonfly_proactor_threads, args.valkey_io_threads, args.requests, args.clients, args.pipeline, args.data_size)
    else:
        plot_ops_chart_single(data_ops, out_filename, args.redis_io_threads, args.keydb_server_threads, args.dragonfly_proactor_threads, args.valkey_io_threads, args.requests, args.clients, args.pipeline, args.data_size)