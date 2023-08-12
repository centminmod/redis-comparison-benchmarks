#!/usr/bin/env python3
import sys

def parse_to_md(filename):
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

    # Convert to markdown table format
    header = "| " + " | ".join(stats_lines[0].split()) + " |\n"
    separator = "| " + " | ".join(["---"] * len(stats_lines[0].split())) + " |\n"
    body = "".join(["| " + " | ".join(line.split()) + " |\n" for line in stats_lines[1:]])

    md_table = header + separator + body

    with open(filename.replace('.txt', '.md'), 'w') as file:
        file.write(md_table)

if __name__ == "__main__":
    parse_to_md(sys.argv[1])
