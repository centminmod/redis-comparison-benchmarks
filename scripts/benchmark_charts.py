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
    """Parse markdown benchmark results into structured DataFrame"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split content by database sections
    sections = re.split(r'\| Databases \| Type \| Ops/sec.*?\n\| --- \| --- \| --- .*?\n', content)
    
    data = []
    current_db = None
    current_threads = None
    
    for line in content.split('\n'):
        if '|' not in line or line.startswith('| ---') or line.startswith('| Databases'):
            continue
            
        parts = [p.strip() for p in line.split('|')[1:-1]]  # Remove empty first/last elements
        if len(parts) < 9:
            continue
            
        # Check if this is a database header line
        if 'Thread' in parts[0]:
            db_info = parts[0].split()
            if 'TLS' in db_info:
                current_db = db_info[0]
                current_threads = int(db_info[2])
            else:
                current_db = db_info[0]
                current_threads = int(db_info[1])
            continue
            
        # Skip if we don't have current database context
        if current_db is None or current_threads is None:
            continue
            
        # Parse data row
        op_type = parts[1]
        if op_type in ['Sets', 'Gets', 'Totals']:
            try:
                row_data = {
                    'Database': current_db,
                    'Threads': current_threads,
                    'Type': op_type,
                    'Ops_sec': float(parts[2]) if parts[2] != '---' else 0,
                    'Hits_sec': float(parts[3]) if parts[3] != '---' else 0,
                    'Misses_sec': float(parts[4]) if parts[4] != '---' else 0,
                    'Avg_Latency': float(parts[5]) if parts[5] != '---' else 0,
                    'p50_Latency': float(parts[6]) if parts[6] != '---' else 0,
                    'p99_Latency': float(parts[7]) if parts[7] != '---' else 0,
                    'p99_9_Latency': float(parts[8]) if parts[8] != '---' else 0,
                    'KB_sec': float(parts[9]) if parts[9] != '---' else 0
                }
                data.append(row_data)
            except (ValueError, IndexError):
                continue
    
    return pd.DataFrame(data)

def setup_style():
    """Configure matplotlib style and colors"""
    plt.style.use('seaborn-v0_8')
    colors = {
        'Redis': '#E74C3C',
        'KeyDB': '#27AE60', 
        'Dragonfly': '#F39C12',
        'Valkey': '#8E44AD'
    }
    return colors

def create_operations_scaling_chart(df, colors, tls_suffix, output_dir):
    """Chart 1: Operations Performance Scaling Line Chart"""
    totals_df = df[df['Type'] == 'Totals']
    
    plt.figure(figsize=(12, 8))
    
    for db in totals_df['Database'].unique():
        db_data = totals_df[totals_df['Database'] == db].sort_values('Threads')
        plt.plot(db_data['Threads'], db_data['Ops_sec'], 
                marker='o', linewidth=3, markersize=8, 
                color=colors[db], label=db)
    
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

def create_grouped_comparison_chart(df, colors, tls_suffix, output_dir):
    """Chart 2: Database Comparison by Thread Count Grouped Bar Chart"""
    totals_df = df[df['Type'] == 'Totals']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    threads = sorted(totals_df['Threads'].unique())
    databases = sorted(totals_df['Database'].unique())
    
    x = np.arange(len(threads))
    width = 0.2
    
    for i, db in enumerate(databases):
        db_data = []
        for thread in threads:
            ops = totals_df[(totals_df['Database'] == db) & (totals_df['Threads'] == thread)]['Ops_sec'].iloc[0]
            db_data.append(ops)
        
        ax.bar(x + i * width, db_data, width, label=db, color=colors[db], alpha=0.8)
    
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

def create_latency_throughput_scatter(df, colors, tls_suffix, output_dir):
    """Chart 3: Latency vs Throughput Trade-off Scatter Plot"""
    totals_df = df[df['Type'] == 'Totals']
    
    plt.figure(figsize=(12, 8))
    
    for db in totals_df['Database'].unique():
        db_data = totals_df[totals_df['Database'] == db]
        
        # Create bubble sizes based on thread count
        sizes = [50 + t * 25 for t in db_data['Threads']]
        
        scatter = plt.scatter(db_data['Avg_Latency'], db_data['Ops_sec'], 
                            s=sizes, alpha=0.7, color=colors[db], label=db, edgecolors='black')
    
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

def create_cache_efficiency_chart(df, colors, tls_suffix, output_dir):
    """Chart 4: Cache Efficiency Stacked Bar Chart"""
    gets_df = df[df['Type'] == 'Gets']
    
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
        ax.bar(x + i * width, hits, width, label=f'{db} Hits', color=colors[db], alpha=0.8)
        ax.bar(x + i * width, misses, width, bottom=hits, label=f'{db} Misses', 
               color=colors[db], alpha=0.4, hatch='///')
    
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

def create_latency_distribution_chart(df, colors, tls_suffix, output_dir):
    """Chart 5: Latency Distribution Comparison Box Plot"""
    totals_df = df[df['Type'] == 'Totals']
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Latency Distribution Comparison{tls_suffix}', fontsize=16, fontweight='bold')
    
    latency_metrics = ['p50_Latency', 'p99_Latency', 'p99_9_Latency', 'Avg_Latency']
    titles = ['p50 Latency', 'p99 Latency', 'p99.9 Latency', 'Average Latency']
    
    for idx, (metric, title) in enumerate(zip(latency_metrics, titles)):
        ax = axes[idx // 2, idx % 2]
        
        data_for_box = []
        labels = []
        colors_list = []
        
        for db in sorted(totals_df['Database'].unique()):
            db_data = totals_df[totals_df['Database'] == db]
            for thread in sorted(db_data['Threads'].unique()):
                thread_data = db_data[db_data['Threads'] == thread]
                if not thread_data.empty:
                    # Create artificial distribution around the actual value for box plot
                    value = thread_data[metric].iloc[0]
                    distribution = np.random.normal(value, value * 0.05, 100)
                    data_for_box.append(distribution)
                    labels.append(f'{db}\n{thread}T')
                    colors_list.append(colors[db])
        
        box_plot = ax.boxplot(data_for_box, labels=labels, patch_artist=True)
        
        for patch, color in zip(box_plot['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel('Latency (ms)', fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-latency-dist{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_radar_chart(df, colors, tls_suffix, output_dir):
    """Performance Radar Chart for each database"""
    totals_df = df[df['Type'] == 'Totals']
    gets_df = df[df['Type'] == 'Gets']
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16), subplot_kw=dict(projection='polar'))
    fig.suptitle(f'Performance Radar Charts{tls_suffix}', fontsize=16, fontweight='bold')
    
    databases = sorted(totals_df['Database'].unique())
    
    for idx, db in enumerate(databases):
        ax = axes[idx // 2, idx % 2]
        
        # Calculate normalized metrics for 8-thread performance
        db_8t_totals = totals_df[(totals_df['Database'] == db) & (totals_df['Threads'] == 8)]
        db_8t_gets = gets_df[(gets_df['Database'] == db) & (gets_df['Threads'] == 8)]
        
        if db_8t_totals.empty or db_8t_gets.empty:
            continue
            
        # Normalize metrics (0-1 scale)
        max_ops = totals_df['Ops_sec'].max()
        min_latency = totals_df['Avg_Latency'].min()
        max_latency = totals_df['Avg_Latency'].max()
        max_hits = gets_df['Hits_sec'].max()
        
        ops_score = db_8t_totals['Ops_sec'].iloc[0] / max_ops
        latency_score = 1 - ((db_8t_totals['Avg_Latency'].iloc[0] - min_latency) / (max_latency - min_latency))
        hit_rate_score = db_8t_gets['Hits_sec'].iloc[0] / max_hits if max_hits > 0 else 0
        consistency_score = 1 - (db_8t_totals['p99_9_Latency'].iloc[0] - db_8t_totals['p50_Latency'].iloc[0]) / max_latency
        
        scores = [ops_score, latency_score, hit_rate_score, consistency_score]
        labels = ['Throughput', 'Low Latency', 'Cache Hit Rate', 'Consistency']
        
        # Add first point at the end to close the polygon
        scores += scores[:1]
        
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        
        ax.plot(angles, scores, 'o-', linewidth=2, color=colors[db], label=db)
        ax.fill(angles, scores, alpha=0.25, color=colors[db])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 1)
        ax.set_title(f'{db} Performance Profile', fontsize=12, fontweight='bold', pad=20)
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-radar{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_heatmap_dashboard(df, colors, tls_suffix, output_dir):
    """Heatmap Dashboard showing normalized performance scores"""
    totals_df = df[df['Type'] == 'Totals']
    
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
            matrix_norm = (matrix - matrix.min()) / (matrix.max() - matrix.min())
        else:
            matrix_norm = 1 - (matrix - matrix.min()) / (matrix.max() - matrix.min())
        
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
            tls_suffix = ''
            
            print("Creating charts...")
            create_operations_scaling_chart(df, colors, tls_suffix, args.output_dir)
            create_grouped_comparison_chart(df, colors, tls_suffix, args.output_dir)
            create_latency_throughput_scatter(df, colors, tls_suffix, args.output_dir)
            create_cache_efficiency_chart(df, colors, tls_suffix, args.output_dir)
            create_latency_distribution_chart(df, colors, tls_suffix, args.output_dir)
            create_performance_radar_chart(df, colors, tls_suffix, args.output_dir)
            create_heatmap_dashboard(df, colors, tls_suffix, args.output_dir)
            print("Non-TLS charts completed!")
        else:
            print(f"File not found: {file_path}")
    
    if args.tls:
        print("Processing TLS results...")
        file_path = os.path.join(args.input_dir, 'combined_all_results_tls.md')
        if os.path.exists(file_path):
            df = parse_markdown_table(file_path)
            tls_suffix = '-tls'
            
            print("Creating TLS charts...")
            create_operations_scaling_chart(df, colors, tls_suffix, args.output_dir)
            create_grouped_comparison_chart(df, colors, tls_suffix, args.output_dir)
            create_latency_throughput_scatter(df, colors, tls_suffix, args.output_dir)
            create_cache_efficiency_chart(df, colors, tls_suffix, args.output_dir)
            create_latency_distribution_chart(df, colors, tls_suffix, args.output_dir)
            create_performance_radar_chart(df, colors, tls_suffix, args.output_dir)
            create_heatmap_dashboard(df, colors, tls_suffix, args.output_dir)
            print("TLS charts completed!")
        else:
            print(f"File not found: {file_path}")
    
    print(f"All charts saved to {args.output_dir}/ with prefix 'advcharts-'")

if __name__ == "__main__":
    main()