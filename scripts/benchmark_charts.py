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
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines and separator lines
        if not line or '---' in line:
            continue
            
        # Skip header lines that start with |
        if line.startswith('|'):
            continue
            
        # Skip if line doesn't contain pipe characters
        if '|' not in line:
            continue
            
        # Split by pipe and clean up
        parts = [p.strip() for p in line.split('|')]
        
        # Remove empty last element if line ends with |
        if len(parts) > 0 and parts[-1] == '':
            parts = parts[:-1]
        
        # Skip if we don't have enough columns (should have at least 10: db_info, type, ops, hits, misses, avg_lat, p50, p99, p99.9, kb)
        if len(parts) < 10:
            print(f"Skipping line {line_num} - not enough columns: {len(parts)} parts: {parts}")
            continue
        
        # Parse the first column which contains database info like "Redis TLS 1 Thread"
        db_info = parts[0]
        op_type = parts[1]
        
        # Skip if this isn't a data row with valid operation type
        if op_type not in ['Sets', 'Gets', 'Totals']:
            print(f"Skipping line {line_num} - invalid op_type: '{op_type}'")
            continue
            
        # Parse database name and thread count from first column
        # Examples: "Redis TLS 1 Thread", "KeyDB 2 Threads", "Dragonfly 4 Threads"
        db_words = db_info.split()
        
        # Find database name (first word that's a known database)
        database = None
        for word in db_words:
            if word in ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']:
                database = word
                break
        
        if not database:
            print(f"Skipping line {line_num} - couldn't find database name in: '{db_info}'")
            continue
            
        # Find thread count (look for number followed by "Thread")
        threads = None
        for i, word in enumerate(db_words):
            if word.isdigit() and i + 1 < len(db_words) and 'Thread' in db_words[i + 1]:
                threads = int(word)
                break
        
        if threads is None:
            print(f"Skipping line {line_num} - couldn't find thread count in: '{db_info}'")
            continue
        
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
                'Database': database,
                'Threads': threads,
                'Type': op_type,
                'Ops_sec': safe_float(parts[2]),
                'Hits_sec': safe_float(parts[3]),
                'Misses_sec': safe_float(parts[4]),
                'Avg_Latency': safe_float(parts[5]),
                'p50_Latency': safe_float(parts[6]),
                'p99_Latency': safe_float(parts[7]),
                'p99_9_Latency': safe_float(parts[8]),
                'KB_sec': safe_float(parts[9])
            }
            data.append(row_data)
            print(f"Added row: {database} {threads}T {op_type} - {row_data['Ops_sec']} ops/sec")
            
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
        print("\nSample data lines:")
        data_lines = [line for line in lines if '|' in line and not line.startswith('|') and '---' not in line]
        for i, line in enumerate(data_lines[:5]):
            print(f"Data line {i+1}: {repr(line.strip())}")
    
    return df

def setup_style():
    """Configure matplotlib style and colors"""
    plt.style.use('default')
    colors = {
        'Redis': '#E74C3C',
        'KeyDB': '#27AE60', 
        'Dragonfly': '#F39C12',
        'Valkey': '#8E44AD'
    }
    return colors

def create_operations_scaling_chart(df, colors, tls_suffix, output_dir):
    """Chart 1: Operations Performance Scaling Line Chart with Better Positioned Data Labels"""
    if df.empty:
        print("DataFrame is empty, skipping operations scaling chart")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping operations scaling chart")
        return
    
    plt.figure(figsize=(12, 8))
    
    # Enhanced offset patterns to avoid overlap - larger offsets and more variation
    label_offsets = {
        0: (0, 25),     # Redis
        1: (-20, 20),   # KeyDB  
        2: (20, 20),    # Dragonfly
        3: (0, -20)     # Valkey
    }
    
    for idx, db in enumerate(totals_df['Database'].unique()):
        db_data = totals_df[totals_df['Database'] == db].sort_values('Threads')
        if not db_data.empty:
            plt.plot(db_data['Threads'], db_data['Ops_sec'], 
                    marker='o', linewidth=3, markersize=8, 
                    color=colors.get(db, '#666666'), label=db)
            
            # Add data labels with enhanced offset positioning and smaller font
            offset = label_offsets.get(idx, (0, 25))
            for x, y in zip(db_data['Threads'], db_data['Ops_sec']):
                plt.annotate(f'{y:,.0f}', (x, y), textcoords="offset points", 
                           xytext=offset, ha='center', fontsize=7, fontweight='bold',  # Smaller font
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='gray'))
    
    plt.xlabel('Thread Count', fontsize=14, fontweight='bold')
    plt.ylabel('Operations per Second', fontsize=14, fontweight='bold')
    plt.title(f'Database Performance Scaling{tls_suffix}', fontsize=16, fontweight='bold')
    plt.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    plt.grid(True, alpha=0.3)
    plt.xticks([1, 2, 4, 8])
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-scaling{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-scaling{tls_suffix}.png")

def create_grouped_comparison_chart(df, colors, tls_suffix, output_dir):
    """Chart 2: Database Comparison by Thread Count Grouped Bar Chart with Wider Spacing"""
    if df.empty:
        print("DataFrame is empty, skipping grouped comparison chart")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping grouped comparison chart")
        return
    
    fig, ax = plt.subplots(figsize=(16, 9))
    
    threads = sorted(totals_df['Threads'].unique())
    databases = sorted(totals_df['Database'].unique())
    
    x = np.arange(len(threads))
    width = 0.15  # Much wider spacing between bars
    
    for i, db in enumerate(databases):
        db_data = []
        for thread in threads:
            thread_data = totals_df[(totals_df['Database'] == db) & (totals_df['Threads'] == thread)]
            if not thread_data.empty:
                db_data.append(thread_data['Ops_sec'].iloc[0])
            else:
                db_data.append(0)
        
        bars = ax.bar(x + i * width, db_data, width, label=db, color=colors.get(db, '#666666'), alpha=0.8)
        
        # Add data labels on bars - NO ROTATION, just better spacing
        for j, bar in enumerate(bars):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + max(db_data) * 0.02,
                       f'{height:,.0f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax.set_xlabel('Thread Count', fontsize=14, fontweight='bold')
    ax.set_ylabel('Operations per Second', fontsize=14, fontweight='bold')
    ax.set_title(f'Database Performance Comparison by Thread Count{tls_suffix}', fontsize=16, fontweight='bold')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(threads)
    ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, axis='y')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-comparison{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-comparison{tls_suffix}.png")

def create_latency_throughput_scatter(df, colors, tls_suffix, output_dir):
    """Chart 3: Latency vs Throughput Trade-off Scatter Plot with Data Labels"""
    if df.empty:
        print("DataFrame is empty, skipping latency throughput scatter")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping latency throughput scatter")
        return
    
    plt.figure(figsize=(14, 8))
    
    for db in totals_df['Database'].unique():
        db_data = totals_df[totals_df['Database'] == db]
        
        if not db_data.empty:
            sizes = [50 + t * 25 for t in db_data['Threads']]
            
            scatter = plt.scatter(db_data['Avg_Latency'], db_data['Ops_sec'], 
                                s=sizes, alpha=0.7, color=colors.get(db, '#666666'), 
                                label=db, edgecolors='black')
            
            # Add data labels showing thread count with smart positioning
            for lat, ops, threads in zip(db_data['Avg_Latency'], db_data['Ops_sec'], db_data['Threads']):
                # Offset based on position to avoid overlap
                offset_x = 8 if lat < 1.0 else -8
                offset_y = 8 if ops < 50000 else -8
                plt.annotate(f'{threads}T', (lat, ops), textcoords="offset points", 
                           xytext=(offset_x, offset_y), ha='center', fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    plt.xlabel('Average Latency (ms)', fontsize=14, fontweight='bold')
    plt.ylabel('Operations per Second', fontsize=14, fontweight='bold')
    plt.title(f'Latency vs Throughput Trade-off{tls_suffix}\n(Bubble size = Thread count)', fontsize=16, fontweight='bold')
    plt.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    plt.grid(True, alpha=0.3)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-tradeoff{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-tradeoff{tls_suffix}.png")

def create_cache_efficiency_chart(df, colors, tls_suffix, output_dir):
    """Chart 4: Cache Efficiency - Hit Rate Percentage and Absolute Values with 45-degree labels and total gets labels"""
    if df.empty:
        print("DataFrame is empty, skipping cache efficiency chart")
        return
        
    gets_df = df[df['Type'] == 'Gets']
    
    if gets_df.empty:
        print("No 'Gets' data found, skipping cache efficiency chart")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    threads = sorted(gets_df['Threads'].unique())
    databases = sorted(gets_df['Database'].unique())
    
    # Chart 1: Hit Rate Percentage - 45 DEGREE ROTATION
    x = np.arange(len(threads))
    width = 0.08
    spacing = 0.04
    max_hit_rate = 0
    
    for i, db in enumerate(databases):
        hit_rates = []
        for thread in threads:
            db_thread_data = gets_df[(gets_df['Database'] == db) & (gets_df['Threads'] == thread)]
            if not db_thread_data.empty:
                hits = db_thread_data['Hits_sec'].iloc[0]
                total_gets = db_thread_data['Ops_sec'].iloc[0]
                hit_rate = (hits / total_gets * 100) if total_gets > 0 else 0
                hit_rates.append(hit_rate)
                max_hit_rate = max(max_hit_rate, hit_rate)
            else:
                hit_rates.append(0)
        
        bar_positions = x + (i * (width + spacing))
        bars = ax1.bar(bar_positions, hit_rates, width, label=db, color=colors.get(db, '#666666'), alpha=0.8)
        
        # Add 45-DEGREE data labels on bars
        for j, bar in enumerate(bars):
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height + max_hit_rate * 0.03,
                        f'{height:.3f}%', ha='center', va='bottom', fontsize=7, fontweight='bold',
                        rotation=45)  # 45-DEGREE ROTATION
            else:
                ax1.text(bar.get_x() + bar.get_width()/2., max_hit_rate * 0.02,
                        '0%', ha='center', va='bottom', fontsize=7, fontweight='bold',
                        rotation=45, alpha=0.6)
    
    ax1.set_xlabel('Thread Count', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Cache Hit Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Cache Hit Rate by Thread Count', fontsize=14, fontweight='bold')
    
    group_centers = x + (len(databases) - 1) * (width + spacing) / 2
    ax1.set_xticks(group_centers)
    ax1.set_xticklabels(threads)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, max_hit_rate * 1.4 if max_hit_rate > 0 else 0.1)
    
    # Chart 2: Absolute Values - ADD LABELS TO TOTAL GETS BARS
    x2 = np.arange(len(databases))
    width2 = 0.08
    spacing2 = 0.04
    
    all_gets = []
    all_hits = []
    
    for thread in threads:
        for db in databases:
            db_thread_data = gets_df[(gets_df['Database'] == db) & (gets_df['Threads'] == thread)]
            if not db_thread_data.empty:
                all_gets.append(db_thread_data['Ops_sec'].iloc[0])
                all_hits.append(db_thread_data['Hits_sec'].iloc[0])
    
    max_gets = max(all_gets) if all_gets else 1
    
    for i, thread in enumerate(threads):
        hits_data = []
        gets_data = []
        
        for db in databases:
            db_thread_data = gets_df[(gets_df['Database'] == db) & (gets_df['Threads'] == thread)]
            if not db_thread_data.empty:
                hits_data.append(db_thread_data['Hits_sec'].iloc[0])
                gets_data.append(db_thread_data['Ops_sec'].iloc[0])
            else:
                hits_data.append(0)
                gets_data.append(0)
        
        bar_positions = x2 + (i * (width2 + spacing2))
        
        # Plot total gets as light background bars WITH LABELS
        gets_bars = ax2.bar(bar_positions, gets_data, width2, 
                           label=f'{thread}T Total Gets', alpha=0.3, color='lightgray', edgecolor='black')
        
        # Add data labels to total gets bars
        for j, (bar, gets) in enumerate(zip(gets_bars, gets_data)):
            if gets > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., gets + max_gets * 0.02,
                        f'{gets:.0f}', ha='center', va='bottom', fontsize=6, fontweight='bold', alpha=0.7)
        
        # Plot hits for ALL databases
        for j, (db, hits, gets) in enumerate(zip(databases, hits_data, gets_data)):
            if gets > 0:
                hit_bar = ax2.bar(bar_positions[j], hits, width2, 
                                 color=colors.get(db, '#666666'), alpha=0.8, edgecolor='black')
                
                # Add data label for hits
                if hits > 0:
                    ax2.text(bar_positions[j], hits + max_gets * 0.005,
                            f'{hits:.0f}', ha='center', va='bottom', fontsize=7, fontweight='bold')
                else:
                    ax2.text(bar_positions[j], max_gets * 0.01,
                            '0', ha='center', va='bottom', fontsize=7, fontweight='bold', alpha=0.6)
    
    # Create legend
    import matplotlib.patches as mpatches
    legend_elements = []
    
    for thread in threads:
        legend_elements.append(mpatches.Patch(color='lightgray', alpha=0.3, label=f'{thread}T Total Gets'))
    
    legend_elements.append(mpatches.Patch(color='white', alpha=0, label=''))
    
    for db in databases:
        legend_elements.append(mpatches.Patch(color=colors.get(db, '#666666'), alpha=0.8, label=f'{db} Hits'))
    
    ax2.set_xlabel('Database', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Operations per Second', fontsize=12, fontweight='bold')
    ax2.set_title('Cache Hits vs Total Gets (Absolute Values)', fontsize=14, fontweight='bold')
    
    group_centers2 = x2 + (len(threads) - 1) * (width2 + spacing2) / 2
    ax2.set_xticks(group_centers2)
    ax2.set_xticklabels(databases)
    ax2.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.suptitle(f'Cache Efficiency Analysis{tls_suffix}', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-cache{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-cache{tls_suffix}.png")

def create_simple_latency_chart(df, colors, tls_suffix, output_dir):
    """Chart 5: Simple Latency Comparison Chart with Better Positioned Data Labels"""
    if df.empty:
        print("DataFrame is empty, skipping latency chart")
        return
        
    totals_df = df[df['Type'] == 'Totals']
    
    if totals_df.empty:
        print("No 'Totals' data found, skipping latency chart")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    threads = sorted(totals_df['Threads'].unique())
    
    # IMPROVED POSITIONING: Position labels based on thread count and value ranges
    # Average Latency Chart
    for idx, db in enumerate(totals_df['Database'].unique()):
        db_data = totals_df[totals_df['Database'] == db].sort_values('Threads')
        if not db_data.empty:
            ax1.plot(db_data['Threads'], db_data['Avg_Latency'], 
                    marker='o', linewidth=3, markersize=8,
                    color=colors.get(db, '#666666'), label=db)
            
            # SMART POSITIONING: alternate above/below based on database index and thread position
            for i, (x, y) in enumerate(zip(db_data['Threads'], db_data['Avg_Latency'])):
                # Determine position based on database index and thread position
                if idx % 2 == 0:  # Even indexed databases (Redis, Dragonfly)
                    offset_y = 15 if i % 2 == 0 else -15
                    offset_x = -10 if i < 2 else 10
                else:  # Odd indexed databases (KeyDB, Valkey)
                    offset_y = -15 if i % 2 == 0 else 15
                    offset_x = 10 if i < 2 else -10
                
                ax1.annotate(f'{y:.2f}', (x, y), textcoords="offset points", 
                           xytext=(offset_x, offset_y), ha='center', fontsize=6, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    ax1.set_xlabel('Thread Count', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Latency (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Average Latency', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(threads)
    
    # p99 Latency Chart
    for idx, db in enumerate(totals_df['Database'].unique()):
        db_data = totals_df[totals_df['Database'] == db].sort_values('Threads')
        if not db_data.empty:
            ax2.plot(db_data['Threads'], db_data['p99_Latency'], 
                    marker='s', linewidth=3, markersize=8,
                    color=colors.get(db, '#666666'), label=db)
            
            # SMART POSITIONING: same pattern but for p99 values
            for i, (x, y) in enumerate(zip(db_data['Threads'], db_data['p99_Latency'])):
                if idx % 2 == 0:  # Even indexed databases
                    offset_y = 15 if i % 2 == 0 else -15
                    offset_x = -10 if i < 2 else 10
                else:  # Odd indexed databases
                    offset_y = -15 if i % 2 == 0 else 15
                    offset_x = 10 if i < 2 else -10
                
                ax2.annotate(f'{y:.2f}', (x, y), textcoords="offset points", 
                           xytext=(offset_x, offset_y), ha='center', fontsize=6, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray'))
    
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
        if idx >= 4:
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
        ('Ops_sec', 'Operations/sec', True),
        ('Avg_Latency', 'Avg Latency (ms)', False),
        ('p99_Latency', 'p99 Latency (ms)', False),
        ('p99_9_Latency', 'p99.9 Latency (ms)', False)
    ]
    
    for idx, (metric, title, higher_better) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]
        
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
        
        im = ax.imshow(matrix_norm, cmap='RdYlGn', aspect='auto', interpolation='nearest')
        
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Performance Score', rotation=270, labelpad=15)
        
        ax.set_xticks(range(len(threads)))
        ax.set_xticklabels([f'{t}T' for t in threads])
        ax.set_yticks(range(len(databases)))
        ax.set_yticklabels(databases)
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Add text annotations with actual values
        for i in range(len(databases)):
            for j in range(len(threads)):
                value = matrix[i, j]
                if value > 0:
                    display_val = f'{value:.0f}' if metric == 'Ops_sec' else f'{value:.2f}'
                    ax.text(j, i, display_val, ha="center", va="center", 
                           color="black", fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-heatmap{tls_suffix}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-heatmap{tls_suffix}.png")

def create_stacked_comparison_chart(df_non_tls, df_tls, colors, output_dir):
    """Chart: Non-TLS vs TLS Stacked Comparison Bar Chart"""
    if df_non_tls.empty and df_tls.empty:
        print("Both DataFrames are empty, skipping stacked comparison chart")
        return
    
    # Get totals data from both datasets
    totals_non_tls = df_non_tls[df_non_tls['Type'] == 'Totals'] if not df_non_tls.empty else pd.DataFrame()
    totals_tls = df_tls[df_tls['Type'] == 'Totals'] if not df_tls.empty else pd.DataFrame()
    
    if totals_non_tls.empty and totals_tls.empty:
        print("No 'Totals' data found in either dataset, skipping stacked comparison chart")
        return
    
    fig, ax = plt.subplots(figsize=(18, 10))
    
    # Get all databases and threads from both datasets
    all_databases = set()
    all_threads = set()
    
    if not totals_non_tls.empty:
        all_databases.update(totals_non_tls['Database'].unique())
        all_threads.update(totals_non_tls['Threads'].unique())
    
    if not totals_tls.empty:
        all_databases.update(totals_tls['Database'].unique())
        all_threads.update(totals_tls['Threads'].unique())
    
    databases = sorted(list(all_databases))
    threads = sorted(list(all_threads))
    
    # Create positions for each thread count with proper spacing
    x = np.arange(len(threads))
    width = 0.18  # Narrower bars for better separation
    spacing = 0.02  # Small gap between bars
    
    for i, db in enumerate(databases):
        # Calculate positions for this database's bars
        # Center the group of bars around each thread position
        offset = (i - (len(databases) - 1) / 2) * (width + spacing)
        bar_positions = x + offset
        
        # Get non-TLS and TLS data for this database
        non_tls_data = []
        tls_data = []
        
        for thread in threads:
            # Non-TLS values
            if not totals_non_tls.empty:
                non_tls_thread_data = totals_non_tls[(totals_non_tls['Database'] == db) & (totals_non_tls['Threads'] == thread)]
                non_tls_val = non_tls_thread_data['Ops_sec'].iloc[0] if not non_tls_thread_data.empty else 0
            else:
                non_tls_val = 0
            
            # TLS values
            if not totals_tls.empty:
                tls_thread_data = totals_tls[(totals_tls['Database'] == db) & (totals_tls['Threads'] == thread)]
                tls_val = tls_thread_data['Ops_sec'].iloc[0] if not tls_thread_data.empty else 0
            else:
                tls_val = 0
            
            non_tls_data.append(non_tls_val)
            tls_data.append(tls_val)
        
        # Create stacked bars
        bars1 = ax.bar(bar_positions, non_tls_data, width, 
                      label=f'{db} Non-TLS', color=colors.get(db, '#666666'), alpha=0.8)
        bars2 = ax.bar(bar_positions, tls_data, width, bottom=non_tls_data,
                      label=f'{db} TLS', color=colors.get(db, '#666666'), alpha=0.6, 
                      hatch='///')
        
        # Add data labels with better positioning
        for j, (bar1, bar2, non_tls_val, tls_val) in enumerate(zip(bars1, bars2, non_tls_data, tls_data)):
            # Non-TLS label (bottom section) - only if value is significant
            if non_tls_val > 5000:  # Only show label if value is large enough
                ax.text(bar1.get_x() + bar1.get_width()/2., non_tls_val/2,
                       f'{non_tls_val:,.0f}', ha='center', va='center', 
                       fontsize=6, fontweight='bold')
            
            # TLS label (top section) - only if value is significant
            if tls_val > 5000:  # Only show label if value is large enough
                ax.text(bar2.get_x() + bar2.get_width()/2., non_tls_val + tls_val/2,
                       f'{tls_val:,.0f}', ha='center', va='center', 
                       fontsize=6, fontweight='bold', color='white')
            
            # Total label above stack
            total = non_tls_val + tls_val
            if total > 0:
                ax.text(bar1.get_x() + bar1.get_width()/2., total + max([sum(x) for x in zip(non_tls_data, tls_data)]) * 0.01,
                       f'{total:,.0f}', ha='center', va='bottom', 
                       fontsize=7, fontweight='bold')
    
    ax.set_xlabel('Thread Count', fontsize=14, fontweight='bold')
    ax.set_ylabel('Operations per Second', fontsize=14, fontweight='bold')
    ax.set_title('Database Performance: Non-TLS vs TLS Stacked Comparison', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(threads)
    
    # Create custom legend with better organization
    legend_elements = []
    for db in databases:
        legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=colors.get(db, '#666666'), alpha=0.8, label=f'{db} Non-TLS'))
        legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=colors.get(db, '#666666'), alpha=0.6, hatch='///', label=f'{db} TLS'))
    
    # Place legend outside the plot area
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9, ncol=1)
    ax.grid(True, alpha=0.3, axis='y')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/advcharts-comparison-stack.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: advcharts-comparison-stack.png")

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
    
    Path(args.output_dir).mkdir(exist_ok=True)
    colors = setup_style()
    
    # Initialize dataframes
    df_non_tls = pd.DataFrame()
    df_tls = pd.DataFrame()
    
    if args.non_tls:
        print("Processing non-TLS results...")
        file_path = os.path.join(args.input_dir, 'combined_all_results.md')
        if os.path.exists(file_path):
            df_non_tls = parse_markdown_table(file_path)
            if not df_non_tls.empty:
                tls_suffix = ''
                print("Creating non-TLS charts...")
                create_operations_scaling_chart(df_non_tls, colors, tls_suffix, args.output_dir)
                create_grouped_comparison_chart(df_non_tls, colors, tls_suffix, args.output_dir)
                create_latency_throughput_scatter(df_non_tls, colors, tls_suffix, args.output_dir)
                create_cache_efficiency_chart(df_non_tls, colors, tls_suffix, args.output_dir)
                create_simple_latency_chart(df_non_tls, colors, tls_suffix, args.output_dir)
                create_performance_radar_chart(df_non_tls, colors, tls_suffix, args.output_dir)
                create_heatmap_dashboard(df_non_tls, colors, tls_suffix, args.output_dir)
                print("Non-TLS charts completed!")
            else:
                print("Failed to parse non-TLS data")
        else:
            print(f"File not found: {file_path}")
    
    if args.tls:
        print("Processing TLS results...")
        file_path = os.path.join(args.input_dir, 'combined_all_results_tls.md')
        if os.path.exists(file_path):
            df_tls = parse_markdown_table(file_path)
            if not df_tls.empty:
                tls_suffix = '-tls'
                print("Creating TLS charts...")
                create_operations_scaling_chart(df_tls, colors, tls_suffix, args.output_dir)
                create_grouped_comparison_chart(df_tls, colors, tls_suffix, args.output_dir)
                create_latency_throughput_scatter(df_tls, colors, tls_suffix, args.output_dir)
                create_cache_efficiency_chart(df_tls, colors, tls_suffix, args.output_dir)
                create_simple_latency_chart(df_tls, colors, tls_suffix, args.output_dir)
                create_performance_radar_chart(df_tls, colors, tls_suffix, args.output_dir)
                create_heatmap_dashboard(df_tls, colors, tls_suffix, args.output_dir)
                print("TLS charts completed!")
            else:
                print("Failed to parse TLS data")
        else:
            print(f"File not found: {file_path}")
    
    # Create stacked comparison chart if both datasets are available
    if args.tls and args.non_tls:
        print("Creating stacked comparison chart...")
        create_stacked_comparison_chart(df_non_tls, df_tls, colors, args.output_dir)
        print("Stacked comparison chart completed!")
    
    print(f"All charts saved to {args.output_dir}/ with prefix 'advcharts-'")

if __name__ == "__main__":
    main()