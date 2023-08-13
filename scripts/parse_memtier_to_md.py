#!/usr/bin/env python3
import sys

def parse_to_md(filename, prefix):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the ALL STATS section
    start_index = None
    end_index = None
    for idx, line in enumerate(lines):
        if "ALL STATS" in line:
            start_index = idx
            break

    if start_index is None:
        raise ValueError(f"'ALL STATS' section not found in {filename}")

    for idx, line in enumerate(lines[start_index:]):
        if line.strip() == "":
            end_index = idx + start_index
            break

    stats_lines = lines[start_index + 2: end_index]

    # Add prefix to the first column
    stats_lines = [f"{prefix} {line}" for line in stats_lines]

    # Convert to markdown table format
    header = f"| {prefix} | Type | Ops/sec | Hits/sec | Misses/sec | Avg Latency | p50 Latency | p99 Latency | p99.9 Latency | KB/sec |\n"
    separator = "| " + " | ".join(["---"] * 10) + " |\n"  # 10 columns
    body = "".join(["| " + " | ".join(line.split()) + " |\n" for line in stats_lines])

    md_table = header + separator + body

    with open(filename.replace('.txt', '.md'), 'w') as file:
        file.write(md_table)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise ValueError("Expected filename and prefix as arguments.")
    parse_to_md(sys.argv[1], sys.argv[2])
