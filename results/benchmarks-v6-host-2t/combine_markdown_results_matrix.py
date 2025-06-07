#!/usr/bin/env python3
import sys
import os

def combine_markdown_files(filenames, prefix, output_dir):
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
            start_index = 0 if idx == 0 else 2  # Skip the header and separator for subsequent files
            for line in lines[start_index:]:
                combined_rows.append(line)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Write the combined results to a new markdown file with the provided prefix
    output_file = f"{output_dir}/combined_{prefix}_results.md"
    with open(output_file, 'w') as file:
        file.writelines(combined_rows)

    print(f"Combined results written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise ValueError("Expected markdown filenames, prefix, and output directory as arguments.")
    
    filenames = sys.argv[1].split()
    prefix = sys.argv[2]
    output_dir = sys.argv[3]
    combine_markdown_files(filenames, prefix, output_dir)