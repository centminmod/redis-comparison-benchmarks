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
        adjusted_header = "|".join(header_parts)
        separator = lines[1]
        
        combined_rows.append(adjusted_header)  # Adjusted header
        combined_rows.append(separator)  # Separator

    # Extract body from each file
    for idx, filename in enumerate(filenames):
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines[2:]:
                if line != adjusted_header and line != separator:
                    combined_rows.append(line)

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
