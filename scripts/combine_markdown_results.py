#!/usr/bin/env python3
import sys

def combine_markdown_files(filenames, prefix):
    combined_rows = []

    # Extract header only from the first file and adjust label to "Databases"
    with open(filenames[0], 'r') as file:
        lines = file.readlines()
        # Adjust the first label in the header
        header_parts = lines[0].split("|")
        header_parts[1] = " Databases "
        combined_rows.append("|".join(header_parts))  # Adjusted header
        combined_rows.append(lines[1])  # Separator

    # Extract body from each file
    for idx, filename in enumerate(filenames):
        with open(filename, 'r') as file:
            lines = file.readlines()
            if idx == 0:  # For the first file, we've already appended the header and separator
                combined_rows.extend(lines[2:])
            else:  # For subsequent files, skip the header and separator
                combined_rows.extend(lines[2:])

    # Write the combined results to a new markdown file with the provided prefix
    output_file = f"./benchmarklogs/combined_{prefix}_results.md"
    with open(output_file, 'w') as file:
        file.writelines(combined_rows)

    print(f"Combined results written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise ValueError("Expected markdown filenames and a prefix as arguments.")
    
    filenames = sys.argv[1].split()
    prefix = sys.argv[2]
    combine_markdown_files(filenames, prefix)
