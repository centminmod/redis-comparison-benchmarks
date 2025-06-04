#!/usr/bin/env python3
"""
Advanced Database Benchmark Visualization Tool
Creates comprehensive charts from Redis/KeyDB/Dragonfly/Valkey benchmark results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse
import os
import re
from pathlib import Path
from matplotlib.patches import Circle
import warnings
warnings.filterwarnings('ignore')

def parse_markdown_table(file_path):
    """Parse markdown benchmark results into structured DataFrame with improved debugging"""
    print(f"Parsing file: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    print(f"File content length: {len(content)} characters")
    
    data = []
    lines = content.split('\n')
    
    current_db = None
    current_threads = None
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines and separator lines
        if not line or '---' in line or line.startswith('| Databases'):
            continue
            
        # Skip if line doesn't contain pipe characters
        if '|' not in line:
            continue
            
        # Split by pipe and clean up
        parts = [p.strip() for p in line.split('|')]
        
        # Remove empty first/last elements that come from leading/trailing pipes
        if len(parts) > 0 and parts[0] == '':
            parts = parts[1:]
        if len(parts) > 0 and parts[-1] == '':
            parts = parts[:-1]
        
        # Skip if we don't have enough columns
        if len(parts) < 9:
            continue
        
        # Check for database header (contains "Thread" in first column)
        first_col = parts[0]
        if 'Thread' in first_col:
            # Parse database name and thread count
            # Examples: "Redis 1 Thread", "KeyDB TLS 2 Threads", "Dragonfly 4 Threads"
            words = first_col.split()
            
            # Find database name (first word that's not TLS)
            db_name = None
            thread_count = None
            
            for i, word in enumerate(words):
                if word in ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']:
                    db_name = word
                    break
            
            # Find thread count (look for number followed by "Thread")
            for i, word in enumerate(words):
                if word.isdigit() and i + 1 < len(words) and 'Thread' in words[i + 1]:
                    thread_count = int(word)
                    break
            
            if db_name and thread_count:
                current_db = db_name
                current_threads = thread_count
                print(f"Found database header: {current_db} with {current_threads} threads")
            continue
        
        # Skip if we don't have current database context
        if current_db is None or current_threads is None:
            continue
            
        # Check if this is a data row with operation type
        if len(parts) >= 9:
            op_type = parts[1] if len(parts) > 1 else parts[0]
            
            if op_type in ['Sets', 'Gets', 'Totals']:
                try:
                    # Parse numeric values, handling "---" as 0
                    def safe_float(val):
                        if val == '---' or val == '':
                            return 0.0
                        try:
                            return float(val)
                        except:
                            return 0.0
                    
                    row_data = {
                        'Database': current_db,
                        'Threads': current_threads,
                        'Type': op_type,
                        'Ops_sec': safe_float(parts[2]),
                        'Hits_sec': safe_float(parts[3]),
                        'Misses_sec': safe_float(parts[4]),
                        'Avg_Latency': safe_float(parts[5]),
                        'p50_Latency': safe_float(parts[6]),
                        'p99_Latency': safe_float(parts[7]),
                        'p99_9_Latency': safe_float(parts[8]),
                        'KB_sec': safe_float(parts[9]) if len(parts) > 9 else 0.0
                    }
                    data.append(row_data)
                    print(f"Added row: {current_db} {current_threads}T {op_type} - {row_data['Ops_sec']} ops/sec")
                    
                except Exception as e:
                    print(f"Error parsing line {line_num}: {line}")
                    print(f"Parts: {parts}")
                    print(f"Error: {e}")
                    continue
    
    df = pd.DataFrame(data)
    print(f"\nParsed {len(df)} rows")
    if len(df) > 0:
        print(f"Columns: {list(df.columns)}")
        print(f"Databases: {df['Database'].unique() if 'Database' in df.columns else 'None'}")
        print(f"Thread counts: {df['Threads'].unique() if 'Threads' in df.columns else 'None'}")
        print(f"Operation types: {df['Type'].unique() if 'Type' in df.columns else 'None'}")
        print("\nFirst few rows:")
        print(df.head())
    else:
        print("No data parsed! Debugging the file content...")
        print("\nFirst 10 lines of file:")
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                if i < 10:
                    print(f"Line {i+1}: {repr(line.strip())}")
    
    return df

def setup_style():
    """Configure matplotlib style and colors"""
    plt.style.use('default')  # Use default instead of seaborn-v0_8 for better compatibility
    colors = {
        'Redis': '#E74C3C',
        'KeyDB': '#27AE60', 
        'Dragonfly': '#F39C12',
        'Valkey': '#8E44AD'
    }
    return colors

def create_operations_scaling_chart(df, colors, tls_suffix, output_dir):
    """Chart 1: Operations Performance Scaling Line Chart"""
    if df.empty:
        print("DataFrame is empty, skipping operations scaling chart")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping operations scaling chart")
        return
    
    plt.figure(figsize=(12, 8))
    
    for db in totals_df['Database'].unique():
        db_data = totals_df[totals_df['Database'] == db].sort_values('Threads')
        if not db_data.empty:
            plt.plot(db_data['Threads'], db_data['Ops_sec'], 
                    marker='o', linewidth=3, markersize=8, 
                    color=colors.get(db, '#666666'), label=db)
    
    plt.xlabel('Thread Count', fontsize=14, fontweight='bold')
    plt.ylabel('Operations per Second', fontsize=14, fontweight='bold')
    plt.title(f'Database Performance Scaling{tls_suffix}', fontsize=16, fontweight='bold')
    plt.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    plt.grid(True, alpha=0.3)
    plt.xticks([1, 2, 4, 8])
    
    # Format y-axis with comma separators
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-scaling{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-scaling{tls_suffix}.png")

def create_grouped_comparison_chart(df, colors, tls_suffix, output_dir):
    """Chart 2: Database Comparison by Thread Count Grouped Bar Chart"""
    if df.empty:
        print("DataFrame is empty, skipping grouped comparison chart")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping grouped comparison chart")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    threads = sorted(totals_df['Threads'].unique())
    databases = sorted(totals_df['Database'].unique())
    
    x = np.arange(len(threads))
    width = 0.2
    
    for i, db in enumerate(databases):
        db_data = []
        for thread in threads:
            thread_data = totals_df[(totals_df['Database'] == db) & (totals_df['Threads'] == thread)]
            if not thread_data.empty:
                db_data.append(thread_data['Ops_sec'].iloc[0])
            else:
                db_data.append(0)
        
        ax.bar(x + i * width, db_data, width, label=db, color=colors.get(db, '#666666'), alpha=0.8)
    
    ax.set_xlabel('Thread Count', fontsize=14, fontweight='bold')
    ax.set_ylabel('Operations per Second', fontsize=14, fontweight='bold')
    ax.set_title(f'Database Performance Comparison by Thread Count{tls_suffix}', fontsize=16, fontweight='bold')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(threads)
    ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-comparison{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-comparison{tls_suffix}.png")

def create_latency_throughput_scatter(df, colors, tls_suffix, output_dir):
    """Chart 3: Latency vs Throughput Trade-off Scatter Plot"""
    if df.empty:
        print("DataFrame is empty, skipping latency throughput scatter")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping latency throughput scatter")
        return
    
    plt.figure(figsize=(12, 8))
    
    for db in totals_df['Database'].unique():
        db_data = totals_df[totals_df['Database'] == db]
        
        if not db_data.empty:
            # Create bubble sizes based on thread count
            sizes = [50 + t * 25 for t in db_data['Threads']]
            
            scatter = plt.scatter(db_data['Avg_Latency'], db_data['Ops_sec'], 
                                s=sizes, alpha=0.7, color=colors.get(db, '#666666'), 
                                label=db, edgecolors='black')
    
    plt.xlabel('Average Latency (ms)', fontsize=14, fontweight='bold')
    plt.ylabel('Operations per Second', fontsize=14, fontweight='bold')
    plt.title(f'Latency vs Throughput Trade-off{tls_suffix}\n(Bubble size = Thread count)', fontsize=16, fontweight='bold')
    plt.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    plt.grid(True, alpha=0.3)
    
    # Format axes
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-tradeoff{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-tradeoff{tls_suffix}.png")

def create_cache_efficiency_chart(df, colors, tls_suffix, output_dir):
    """Chart 4: Cache Efficiency Stacked Bar Chart"""
    if df.empty:
        print("DataFrame is empty, skipping cache efficiency chart")
        return
        
    gets_df = df[df['Type'] == 'Gets']
    
    if gets_df.empty:
        print("No 'Gets' data found, skipping cache efficiency chart")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    threads = sorted(gets_df['Threads'].unique())
    databases = sorted(gets_df['Database'].unique())
    
    x = np.arange(len(threads))
    width = 0.2
    
    for i, db in enumerate(databases):
        hits = []
        misses = []
        for thread in threads:
            db_thread_data = gets_df[(gets_df['Database'] == db) & (gets_df['Threads'] == thread)]
            if not db_thread_data.empty:
                hits.append(db_thread_data['Hits_sec'].iloc[0])
                misses.append(db_thread_data['Misses_sec'].iloc[0])
            else:
                hits.append(0)
                misses.append(0)
        
        # Stack hits and misses
        ax.bar(x + i * width, hits, width, label=f'{db} Hits', color=colors.get(db, '#666666'), alpha=0.8)
        ax.bar(x + i * width, misses, width, bottom=hits, label=f'{db} Misses', 
               color=colors.get(db, '#666666'), alpha=0.4, hatch='///')
    
    ax.set_xlabel('Thread Count', fontsize=14, fontweight='bold')
    ax.set_ylabel('Operations per Second', fontsize=14, fontweight='bold')
    ax.set_title(f'Cache Efficiency: Hits vs Misses{tls_suffix}', fontsize=16, fontweight='bold')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(threads)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-cache{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-cache{tls_suffix}.png")

def create_simple_latency_chart(df, colors, tls_suffix, output_dir):
    """Chart 5: Simple Latency Comparison Chart"""
    if df.empty:
        print("DataFrame is empty, skipping latency chart")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping latency chart")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Average Latency Chart
    threads = sorted(totals_df['Threads'].unique())
    for db in totals_df['Database'].unique():
        db_data = totals_df[totals_df['Database'] == db].sort_values('Threads')
        if not db_data.empty:
            ax1.plot(db_data['Threads'], db_data['Avg_Latency'], 
                    marker='o', linewidth=3, markersize=8,
                    color=colors.get(db, '#666666'), label=db)
    
    ax1.set_xlabel('Thread Count', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Latency (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Average Latency', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(threads)
    
    # p99 Latency Chart
    for db in totals_df['Database'].unique():
        db_data = totals_df[totals_df['Database'] == db].sort_values('Threads')
        if not db_data.empty:
            ax2.plot(db_data['Threads'], db_data['p99_Latency'], 
                    marker='s', linewidth=3, markersize=8,
                    color=colors.get(db, '#666666'), label=db)
    
    ax2.set_xlabel('Thread Count', fontsize=12, fontweight='bold')
    ax2.set_ylabel('p99 Latency (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('p99 Latency', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(threads)
    
    plt.suptitle(f'Latency Comparison{tls_suffix}', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-latency-dist{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-latency-dist{tls_suffix}.png")

def create_performance_radar_chart(df, colors, tls_suffix, output_dir):
    """Performance Radar Chart for each database"""
    if df.empty:
        print("DataFrame is empty, skipping radar chart")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    gets_df = df[df['Type'] == 'Gets']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping radar chart")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16), subplot_kw=dict(projection='polar'))
    fig.suptitle(f'Performance Radar Charts{tls_suffix}', fontsize=16, fontweight='bold')
    
    databases = sorted(totals_df['Database'].unique())
    
    for idx, db in enumerate(databases):
        if idx >= 4:  # Only handle up to 4 databases
            break
            
        ax = axes[idx // 2, idx % 2]
        
        # Calculate normalized metrics for 8-thread performance (or highest available)
        max_threads = totals_df['Threads'].max()
        db_max_totals = totals_df[(totals_df['Database'] == db) & (totals_df['Threads'] == max_threads)]
        db_max_gets = gets_df[(gets_df['Database'] == db) & (gets_df['Threads'] == max_threads)]
        
        if db_max_totals.empty:
            continue
            
        # Normalize metrics (0-1 scale)
        max_ops = totals_df['Ops_sec'].max()
        min_latency = totals_df['Avg_Latency'].min()
        max_latency = totals_df['Avg_Latency'].max()
        max_hits = gets_df['Hits_sec'].max() if not gets_df.empty else 1
        
        ops_score = db_max_totals['Ops_sec'].iloc[0] / max_ops if max_ops > 0 else 0
        latency_score = 1 - ((db_max_totals['Avg_Latency'].iloc[0] - min_latency) / (max_latency - min_latency)) if max_latency > min_latency else 1
        hit_rate_score = db_max_gets['Hits_sec'].iloc[0] / max_hits if not db_max_gets.empty and max_hits > 0 else 0
        consistency_score = 1 - (db_max_totals['p99_9_Latency'].iloc[0] - db_max_totals['p50_Latency'].iloc[0]) / max_latency if max_latency > 0 else 0
        
        scores = [ops_score, latency_score, hit_rate_score, max(0, consistency_score)]
        labels = ['Throughput', 'Low Latency', 'Cache Hit Rate', 'Consistency']
        
        # Add first point at the end to close the polygon
        scores += scores[:1]
        
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        
        ax.plot(angles, scores, 'o-', linewidth=2, color=colors.get(db, '#666666'), label=db)
        ax.fill(angles, scores, alpha=0.25, color=colors.get(db, '#666666'))
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 1)
        ax.set_title(f'{db} Performance Profile', fontsize=12, fontweight='bold', pad=20)
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-radar{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-radar{tls_suffix}.png")

def create_heatmap_dashboard(df, colors, tls_suffix, output_dir):
    """Heatmap Dashboard showing normalized performance scores"""
    if df.empty:
        print("DataFrame is empty, skipping heatmap")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping heatmap")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Performance Heatmap Dashboard{tls_suffix}', fontsize=16, fontweight='bold')
    
    databases = sorted(totals_df['Database'].unique())
    threads = sorted(totals_df['Threads'].unique())
    
    metrics = [
        ('Ops_sec', 'Operations/sec', True),  # True = higher is better
        ('Avg_Latency', 'Avg Latency (ms)', False),  # False = lower is better
        ('p99_Latency', 'p99 Latency (ms)', False),
        ('p99_9_Latency', 'p99.9 Latency (ms)', False)
    ]
    
    for idx, (metric, title, higher_better) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]
        
        # Create matrix
        matrix = np.zeros((len(databases), len(threads)))
        
        for i, db in enumerate(databases):
            for j, thread in enumerate(threads):
                db_thread = totals_df[(totals_df['Database'] == db) & (totals_df['Threads'] == thread)]
                if not db_thread.empty:
                    matrix[i, j] = db_thread[metric].iloc[0]
        
        # Normalize matrix (0-1 scale)
        if higher_better:
            matrix_norm = (matrix - matrix.min()) / (matrix.max() - matrix.min()) if matrix.max() > matrix.min() else np.ones_like(matrix)
        else:
            matrix_norm = 1 - (matrix - matrix.min()) / (matrix.max() - matrix.min()) if matrix.max() > matrix.min() else np.ones_like(matrix)
        
        # Create heatmap
        im = ax.imshow(matrix_norm, cmap='RdYlGn', aspect='auto', interpolation='nearest')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Performance Score', rotation=270, labelpad=15)
        
        # Set ticks and labels
        ax.set_xticks(range(len(threads)))
        ax.set_xticklabels([f'{t}T' for t in threads])
        ax.set_yticks(range(len(databases)))
        ax.set_yticklabels(databases)
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Add text annotations
        for i in range(len(databases)):
            for j in range(len(threads)):
                text = ax.text(j, i, f'{matrix[i, j]:.0f}', 
                             ha="center", va="center", color="black", fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-heatmap{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-heatmap{tls_suffix}.png")

def main():
    parser = argparse.ArgumentParser(description='Generate advanced database benchmark charts')
    parser.add_argument('--tls', action='store_true', help='Process TLS benchmark results')
    parser.add_argument('--non-tls', action='store_true', help='Process non-TLS benchmark results')
    parser.add_argument('--input-dir', default='.', help='Input directory containing markdown files')
    parser.add_argument('--output-dir', default='benchmarklogs', help='Output directory for charts')
    
    args = parser.parse_args()
    
    if not args.tls and not args.non_tls:
        print("Please specify --tls or --non-tls (or both)")
        return
    
    # Create output directory
    Path(args.output_dir).mkdir(exist_ok=True)
    
    # Setup styling
    colors = setup_style()
    
    if args.non_tls:
        print("Processing non-TLS results...")
        file_path = os.path.join(args.input_dir, 'combined_all_results.md')
        if os.path.exists(file_path):
            df = parse_markdown_table(file_path)
            if not df.empty:
                tls_suffix = ''
                
                print("Creating charts...")
                create_operations_scaling_chart(df, colors, tls_suffix, args.output_dir)
                create_grouped_comparison_chart(df, colors, tls_suffix, args.output_dir)
                create_latency_throughput_scatter(df, colors, tls_suffix, args.output_dir)
                create_cache_efficiency_chart(df, colors, tls_suffix, args.output_dir)
                create_simple_latency_chart(df, colors, tls_suffix, args.output_dir)
                create_performance_radar_chart(df, colors, tls_suffix, args.output_dir)
                create_heatmap_dashboard(df, colors, tls_suffix, args.output_dir)
                print("Non-TLS charts completed!")
            else:
                print("Failed to parse non-TLS data")
        else:
            print(f"File not found: {file_path}")
    
    if args.tls:
        print("Processing TLS results...")
        file_path = os.path.join(args.input_dir, 'combined_all_results_tls.md')
        if os.path.exists(file_path):
            df = parse_markdown_table(file_path)
            if not df.empty:
                tls_suffix = '-tls'
                
                print("Creating TLS charts...")
                create_operations_scaling_chart(df, colors, tls_suffix, args.output_dir)
                create_grouped_comparison_chart(df, colors, tls_suffix, args.output_dir)
                create_latency_throughput_scatter(df, colors, tls_suffix, args.output_dir)
                create_cache_efficiency_chart(df, colors, tls_suffix, args.output_dir)
                create_simple_latency_chart(df, colors, tls_suffix, args.output_dir)
                create_performance_radar_chart(df, colors, tls_suffix, args.output_dir)
                create_heatmap_dashboard(df, colors, tls_suffix, args.output_dir)
                print("TLS charts completed!")
            else:
                print("Failed to parse TLS data")
        else:
            print(f"File not found: {file_path}")
    
    print(f"All charts saved to {args.output_dir}/ with prefix 'advcharts-'")

if __name__ == "__main__":
    main()