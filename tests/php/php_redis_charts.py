#!/usr/bin/env python3
"""
Enhanced PHP Redis Benchmark Charts Generator with Statistical Analysis
Creates comprehensive charts from PHP-based WordPress Redis test results with 5-run statistics
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import glob
import os
from pathlib import Path
import argparse
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnhancedPHPRedisChartsGenerator:
    def __init__(self, results_dir, output_dir):
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Enhanced styling
        plt.style.use('default')
        self.colors = {
            'Redis': '#E74C3C',
            'KeyDB': '#27AE60', 
            'Dragonfly': '#F39C12',
            'Valkey': '#8E44AD'
        }
        
        self.quality_colors = {
            'excellent': '#2ECC71',  # Green
            'good': '#F1C40F',       # Yellow
            'fair': '#E67E22',       # Orange
            'poor': '#E74C3C'        # Red
        }
        
        # Chart configuration
        self.dpi = 300
        self.bbox_inches = 'tight'
        
    def load_test_results(self):
        """Load all JSON test results with enhanced statistical metadata handling"""
        results = {}
        metadata = {}
        raw_data = {}
        
        print(f"Loading results from {self.results_dir}...")
        
        json_files = list(self.results_dir.glob("*.json"))
        if not json_files:
            print(f"No JSON files found in {self.results_dir}")
            return {}, {}, {}
            
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                test_name = data.get('test_name', 'Unknown Test')
                
                # Handle both aggregated and raw results
                if '_raw' in json_file.name:
                    # Raw iterations data
                    raw_data[test_name] = data
                    continue
                
                # Regular aggregated results
                if 'results' in data:
                    if test_name not in results:
                        results[test_name] = []
                    results[test_name].extend(data['results'])
                    
                    # Enhanced metadata with statistical info
                    metadata[test_name] = {
                        'timestamp': data.get('timestamp'),
                        'php_version': data.get('php_version'),
                        'test_configuration': data.get('test_configuration', {}),
                        'test_methodology': data.get('test_methodology', {}),
                        'results_count': data.get('results_count', len(data['results'])),
                        'thread_variant': data.get('thread_variant', 'unknown'),
                        'thread_config': data.get('thread_config', {})
                    }
                
                print(f"Loaded {len(data.get('results', [data]))} results from {json_file.name}")
                
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue
        
        print(f"Total test types loaded: {len(results)}")
        for test_name, test_results in results.items():
            print(f"  {test_name}: {len(test_results)} results")
            
        return results, metadata, raw_data

    def create_statistical_performance_chart(self, results, metadata):
        """Enhanced performance chart with error bars and quality indicators"""
        if not results:
            print("No results to chart")
            return
            
        # Check for TLS data
        has_tls_data = False
        for test_data in results.values():
            if any(r.get('tls', False) for r in test_data):
                has_tls_data = True
                break
        
        # Determine chart layout
        if has_tls_data:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(12, 10))
            ax2 = None
        
        # Get metadata for title
        first_test = next(iter(metadata.values())) if metadata else {}
        php_version = first_test.get('php_version', 'Unknown')
        iterations = first_test.get('test_methodology', {}).get('iterations_per_test', 1)
        thread_variant = first_test.get('thread_variant', 'unknown')
        
        tls_status = "with TLS" if has_tls_data else "non-TLS only"
        fig.suptitle(f'WordPress Redis Tests - Statistical Performance Analysis\n'
                    f'PHP {php_version} | {iterations} iterations per test | Thread variant: {thread_variant} | {tls_status}', 
                    fontsize=16, fontweight='bold')
        
        databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
        
        # Collect data for non-TLS chart
        non_tls_ops = []
        non_tls_errors = []
        non_tls_qualities = []
        
        for db in databases:
            db_results = []
            for test_data in results.values():
                db_result = next((r for r in test_data if r['database'] == db and not r.get('tls', False)), None)
                if db_result:
                    db_results.append(db_result)
            
            if db_results:
                # Use the most recent result or average if multiple tests
                result = db_results[0] if len(db_results) == 1 else self._average_results(db_results)
                ops = result['ops_per_sec']
                error = result.get('ops_per_sec_stddev', 0)
                quality = result.get('measurement_quality', 'unknown')
                
                non_tls_ops.append(ops)
                non_tls_errors.append(error)
                non_tls_qualities.append(quality)
            else:
                non_tls_ops.append(0)
                non_tls_errors.append(0)
                non_tls_qualities.append('unknown')
        
        # Plot non-TLS results with error bars and quality colors
        x = np.arange(len(databases))
        bars1 = ax1.bar(x, non_tls_ops, 
                       yerr=non_tls_errors, 
                       capsize=5,
                       color=[self.quality_colors.get(q, '#CCCCCC') for q in non_tls_qualities],
                       alpha=0.8, 
                       label='Non-TLS')
        
        ax1.set_title('Non-TLS Performance with Statistical Error Bars', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Operations/sec')
        ax1.set_xticks(x)
        ax1.set_xticklabels(databases)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels with quality indicators
        for i, (bar, ops, quality) in enumerate(zip(bars1, non_tls_ops, non_tls_qualities)):
            if ops > 0:
                quality_symbol = {'excellent': '🟢', 'good': '🟡', 'fair': '🟠', 'poor': '🔴'}.get(quality, '⚪')
                ax1.annotate(f'{int(ops)}\n{quality_symbol}',
                           xy=(bar.get_x() + bar.get_width() / 2, ops),
                           xytext=(0, 10),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Create legend for quality indicators
        legend_elements = [plt.Rectangle((0,0),1,1, color=color, alpha=0.8, label=f'{quality.title()} (CV {threshold})')
                          for quality, (color, threshold) in zip(
                              ['excellent', 'good', 'fair', 'poor'],
                              [(self.quality_colors['excellent'], '<2%'),
                               (self.quality_colors['good'], '<5%'),
                               (self.quality_colors['fair'], '<10%'),
                               (self.quality_colors['poor'], '≥10%')])]
        ax1.legend(handles=legend_elements, loc='upper right', title='Measurement Quality')
        
        # TLS chart if data available
        if has_tls_data and ax2 is not None:
            tls_ops = []
            tls_errors = []
            tls_qualities = []
            
            for db in databases:
                db_results = []
                for test_data in results.values():
                    db_result = next((r for r in test_data if r['database'] == db and r.get('tls', False)), None)
                    if db_result:
                        db_results.append(db_result)
                
                if db_results:
                    result = db_results[0] if len(db_results) == 1 else self._average_results(db_results)
                    ops = result['ops_per_sec']
                    error = result.get('ops_per_sec_stddev', 0)
                    quality = result.get('measurement_quality', 'unknown')
                    
                    tls_ops.append(ops)
                    tls_errors.append(error)
                    tls_qualities.append(quality)
                else:
                    tls_ops.append(0)
                    tls_errors.append(0)
                    tls_qualities.append('unknown')
            
            bars2 = ax2.bar(x, tls_ops, 
                           yerr=tls_errors, 
                           capsize=5,
                           color=[self.quality_colors.get(q, '#CCCCCC') for q in tls_qualities],
                           alpha=0.8, 
                           label='TLS')
            
            ax2.set_title('TLS Performance with Statistical Error Bars', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Operations/sec')
            ax2.set_xticks(x)
            ax2.set_xticklabels(databases)
            ax2.grid(axis='y', alpha=0.3)
            
            # Add value labels for TLS
            for i, (bar, ops, quality) in enumerate(zip(bars2, tls_ops, tls_qualities)):
                if ops > 0:
                    quality_symbol = {'excellent': '🟢', 'good': '🟡', 'fair': '🟠', 'poor': '🔴'}.get(quality, '⚪')
                    ax2.annotate(f'{int(ops)}\n{quality_symbol}',
                               xy=(bar.get_x() + bar.get_width() / 2, ops),
                               xytext=(0, 10),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_statistical_performance.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
        plt.close()
        print(f"Generated: {output_file}")

    def create_measurement_reliability_chart(self, results, metadata):
        """New: Chart showing measurement reliability and consistency"""
        if not results:
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Get metadata
        first_test = next(iter(metadata.values())) if metadata else {}
        iterations = first_test.get('test_methodology', {}).get('iterations_per_test', 1)
        thread_variant = first_test.get('thread_variant', 'unknown')
        
        fig.suptitle(f'Measurement Reliability Analysis - {iterations} iterations per test\n'
                    f'Thread variant: {thread_variant}', 
                    fontsize=16, fontweight='bold')
        
        databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
        
        # Collect CV data for reliability analysis
        non_tls_cvs = []
        tls_cvs = []
        quality_counts = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for db in databases:
            # Non-TLS CV
            non_tls_results = []
            for test_data in results.values():
                result = next((r for r in test_data if r['database'] == db and not r.get('tls', False)), None)
                if result:
                    non_tls_results.append(result)
            
            if non_tls_results:
                result = non_tls_results[0]
                cv = result.get('ops_per_sec_cv', 0) * 100
                quality = result.get('measurement_quality', 'unknown')
                non_tls_cvs.append(cv)
                if quality in quality_counts:
                    quality_counts[quality] += 1
            else:
                non_tls_cvs.append(0)
            
            # TLS CV
            tls_results = []
            for test_data in results.values():
                result = next((r for r in test_data if r['database'] == db and r.get('tls', False)), None)
                if result:
                    tls_results.append(result)
            
            if tls_results:
                result = tls_results[0]
                cv = result.get('ops_per_sec_cv', 0) * 100
                tls_cvs.append(cv)
            else:
                tls_cvs.append(0)
        
        # Chart 1: Coefficient of Variation comparison
        x = np.arange(len(databases))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, non_tls_cvs, width, label='Non-TLS', alpha=0.8, color='lightblue')
        if any(cv > 0 for cv in tls_cvs):
            bars2 = ax1.bar(x + width/2, tls_cvs, width, label='TLS', alpha=0.8, color='lightcoral')
        
        ax1.set_title('Coefficient of Variation (Lower = More Reliable)')
        ax1.set_ylabel('CV (%)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(databases)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add threshold lines
        ax1.axhline(y=2, color='green', linestyle='--', alpha=0.7, label='Excellent (2%)')
        ax1.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Good (5%)')
        ax1.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Fair (10%)')
        
        # Add value labels
        for bars in [bars1] + ([bars2] if any(cv > 0 for cv in tls_cvs) else []):
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.annotate(f'{height:.1f}%',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=9)
        
        # Chart 2: Quality distribution pie chart
        quality_labels = [f'{q.title()}\n({count} tests)' for q, count in quality_counts.items() if count > 0]
        quality_values = [count for count in quality_counts.values() if count > 0]
        quality_colors_list = [self.quality_colors[q] for q, count in quality_counts.items() if count > 0]
        
        if quality_values:
            ax2.pie(quality_values, labels=quality_labels, colors=quality_colors_list, 
                   autopct='%1.1f%%', startangle=90)
            ax2.set_title('Measurement Quality Distribution')
        else:
            ax2.text(0.5, 0.5, 'No quality data available', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Measurement Quality Distribution')
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_measurement_reliability.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
        plt.close()
        print(f"Generated: {output_file}")

    def create_iteration_variance_chart(self, raw_data):
        """New: Show variance across individual iterations"""
        if not raw_data:
            print("No raw data available for iteration analysis")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        fig.suptitle('Individual Iteration Performance Analysis\n'
                    'Showing consistency across test iterations', 
                    fontsize=16, fontweight='bold')
        
        databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
        
        for i, db in enumerate(databases):
            ax = axes[i]
            
            # Find raw data for this database
            for test_name, raw_test_data in raw_data.items():
                db_data = None
                if 'databases' in raw_test_data:
                    for db_key, db_info in raw_test_data['databases'].items():
                        if db_info['database'] == db and not db_info.get('tls', False):
                            db_data = db_info
                            break
                
                if db_data and 'iterations' in db_data:
                    iterations = db_data['iterations']
                    iteration_nums = [it['iteration'] for it in iterations]
                    ops_per_sec = [it['ops_per_sec'] for it in iterations]
                    
                    # Plot individual iterations
                    ax.plot(iteration_nums, ops_per_sec, 'o-', alpha=0.7, linewidth=2, markersize=8)
                    
                    # Add mean line
                    mean_ops = np.mean(ops_per_sec)
                    ax.axhline(y=mean_ops, color='red', linestyle='--', alpha=0.8, 
                              label=f'Mean: {int(mean_ops)}')
                    
                    # Add confidence band
                    std_ops = np.std(ops_per_sec, ddof=1)
                    ax.fill_between(iteration_nums, 
                                  mean_ops - std_ops, mean_ops + std_ops, 
                                  alpha=0.2, color='gray', label=f'±1σ: ±{int(std_ops)}')
                    
                    ax.set_title(f'{db} - Iteration Consistency')
                    ax.set_xlabel('Iteration Number')
                    ax.set_ylabel('Operations/sec')
                    ax.grid(True, alpha=0.3)
                    ax.legend()
                    
                    # Calculate and display CV
                    cv = (std_ops / mean_ops) * 100 if mean_ops > 0 else 0
                    ax.text(0.02, 0.98, f'CV: {cv:.1f}%', 
                           transform=ax.transAxes, fontsize=10, fontweight='bold',
                           verticalalignment='top', 
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    break
            else:
                ax.text(0.5, 0.5, f'No raw data\navailable for {db}', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f'{db} - No Data')
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_iteration_variance.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
        plt.close()
        print(f"Generated: {output_file}")

    def create_confidence_interval_chart(self, results, metadata):
        """New: Chart showing confidence intervals for performance measurements"""
        if not results:
            return
            
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        
        # Get metadata
        first_test = next(iter(metadata.values())) if metadata else {}
        iterations = first_test.get('test_methodology', {}).get('iterations_per_test', 1)
        thread_variant = first_test.get('thread_variant', 'unknown')
        
        fig.suptitle(f'95% Confidence Intervals for Performance Measurements\n'
                    f'{iterations} iterations per test | Thread variant: {thread_variant}', 
                    fontsize=16, fontweight='bold')
        
        databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
        y_positions = []
        labels = []
        
        y_pos = 0
        for db in databases:
            # Non-TLS data
            non_tls_results = []
            for test_data in results.values():
                result = next((r for r in test_data if r['database'] == db and not r.get('tls', False)), None)
                if result:
                    non_tls_results.append(result)
            
            if non_tls_results:
                result = non_tls_results[0]
                mean_ops = result['ops_per_sec']
                ci = result.get('ops_per_sec_confidence_interval_95', {})
                
                if isinstance(ci, dict) and 'lower' in ci and 'upper' in ci:
                    lower = ci['lower']
                    upper = ci['upper']
                    margin = ci.get('margin_error', (upper - lower) / 2)
                    
                    # Plot confidence interval
                    ax.errorbar(mean_ops, y_pos, xerr=margin, 
                              fmt='o', markersize=10, capsize=8, capthick=2,
                              color=self.colors.get(db, '#666666'), alpha=0.8)
                    
                    # Add text annotation
                    ax.text(mean_ops, y_pos + 0.1, f'{int(mean_ops)}±{int(margin)}', 
                           ha='center', va='bottom', fontweight='bold')
                    
                    y_positions.append(y_pos)
                    labels.append(f'{db} (Non-TLS)')
                    y_pos += 1
            
            # TLS data if available
            tls_results = []
            for test_data in results.values():
                result = next((r for r in test_data if r['database'] == db and r.get('tls', False)), None)
                if result:
                    tls_results.append(result)
            
            if tls_results:
                result = tls_results[0]
                mean_ops = result['ops_per_sec']
                ci = result.get('ops_per_sec_confidence_interval_95', {})
                
                if isinstance(ci, dict) and 'lower' in ci and 'upper' in ci:
                    lower = ci['lower']
                    upper = ci['upper']
                    margin = ci.get('margin_error', (upper - lower) / 2)
                    
                    # Plot confidence interval with different style
                    ax.errorbar(mean_ops, y_pos, xerr=margin, 
                              fmt='s', markersize=8, capsize=8, capthick=2,
                              color=self.colors.get(db, '#666666'), alpha=0.6,
                              linestyle='--')
                    
                    ax.text(mean_ops, y_pos + 0.1, f'{int(mean_ops)}±{int(margin)}', 
                           ha='center', va='bottom', fontweight='bold')
                    
                    y_positions.append(y_pos)
                    labels.append(f'{db} (TLS)')
                    y_pos += 1
        
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Operations per Second')
        ax.set_ylabel('Database Configuration')
        ax.grid(True, alpha=0.3)
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='gray', linestyle='-', markersize=8, label='Non-TLS'),
            Line2D([0], [0], marker='s', color='gray', linestyle='--', markersize=6, label='TLS')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_confidence_intervals.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
        plt.close()
        print(f"Generated: {output_file}")

    def create_enhanced_summary_report(self, results, metadata, raw_data):
        """Enhanced summary report with statistical analysis"""
        if not results:
            print("No results to summarize")
            return
        
        # Check for TLS data
        has_tls_data = False
        for test_data in results.values():
            if any(r.get('tls', False) for r in test_data):
                has_tls_data = True
                break
            
        # Get overall metadata
        first_test = next(iter(metadata.values())) if metadata else {}
        php_version = first_test.get('php_version', 'Unknown')
        test_config = first_test.get('test_configuration', {})
        test_methodology = first_test.get('test_methodology', {})
        thread_variant = first_test.get('thread_variant', 'unknown')
        iterations = test_methodology.get('iterations_per_test', 1)
        
        tls_status = "with TLS" if has_tls_data else "non-TLS only"
        report = f"# Enhanced WordPress Redis Benchmark Results ({tls_status})\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**PHP Version:** {php_version}\n"
        report += f"**Thread Variant:** {thread_variant}\n"
        report += f"**Test Methodology:** {iterations} iterations per test with statistical analysis\n\n"
        
        # Statistical methodology section
        report += "## Statistical Methodology\n\n"
        report += f"- **Iterations per Test:** {iterations}\n"
        report += f"- **Statistical Measures:** Standard deviation, coefficient of variation, 95% confidence intervals\n"
        report += f"- **Quality Assessment:** Based on coefficient of variation thresholds\n"
        if test_methodology.get('iteration_pause_ms'):
            report += f"- **Iteration Pause:** {test_methodology['iteration_pause_ms']}ms between iterations\n"
        report += "\n"
        
        # Quality thresholds explanation
        report += "### Measurement Quality Thresholds\n\n"
        quality_thresholds = test_methodology.get('quality_thresholds', {
            'excellent': 0.02, 'good': 0.05, 'fair': 0.10
        })
        report += f"- **🟢 Excellent:** CV < {quality_thresholds.get('excellent', 0.02)*100:.0f}%\n"
        report += f"- **🟡 Good:** CV < {quality_thresholds.get('good', 0.05)*100:.0f}%\n"
        report += f"- **🟠 Fair:** CV < {quality_thresholds.get('fair', 0.10)*100:.0f}%\n"
        report += f"- **🔴 Poor:** CV ≥ {quality_thresholds.get('fair', 0.10)*100:.0f}%\n\n"
        
        # Enhanced performance table
        report += "## Detailed Performance Results\n\n"
        headers = [
            'Database', 'Mode', 'Ops/sec', '±StdDev', 'CV%', 'Quality', 
            'Latency(ms)', '±StdDev', '95% CI Lower', '95% CI Upper', 'Iterations'
        ]
        
        report += "| " + " | ".join(headers) + " |\n"
        report += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        for test_name, test_data in results.items():
            for result in test_data:
                mode = "TLS" if result.get('tls', False) else "Non-TLS"
                ci = result.get('ops_per_sec_confidence_interval_95', {})
                
                # Quality indicator
                quality = result.get('measurement_quality', 'unknown')
                quality_icon = {'excellent': '🟢', 'good': '🟡', 'fair': '🟠', 'poor': '🔴'}.get(quality, '⚪')
                
                row = [
                    result['database'],
                    mode,
                    f"{result['ops_per_sec']:.0f}",
                    f"±{result.get('ops_per_sec_stddev', 0):.0f}",
                    f"{(result.get('ops_per_sec_cv', 0) * 100):.1f}%",
                    f"{quality_icon} {quality}",
                    f"{result['avg_latency']:.3f}",
                    f"±{result.get('latency_stddev', 0):.3f}",
                    f"{ci.get('lower', 0):.0f}",
                    f"{ci.get('upper', 0):.0f}",
                    str(result.get('iterations_count', iterations))
                ]
                
                report += "| " + " | ".join(row) + " |\n"
        
        # Statistical insights section
        report += "\n## Statistical Insights\n\n"
        
        all_results = []
        for test_data in results.values():
            all_results.extend(test_data)
        
        if all_results:
            # Reliability analysis
            reliable_results = [r for r in all_results if r.get('measurement_quality', 'poor') != 'poor']
            total_tests = len(all_results)
            reliable_count = len(reliable_results)
            
            report += f"### Measurement Reliability\n\n"
            report += f"- **Total measurements:** {total_tests}\n"
            report += f"- **Reliable measurements:** {reliable_count}/{total_tests} ({(reliable_count/total_tests)*100:.1f}%)\n"
            
            if reliable_count < total_tests:
                unreliable_count = total_tests - reliable_count
                report += f"- **⚠️ Unreliable measurements:** {unreliable_count} (high variability detected)\n"
                report += f"- **Recommendation:** Consider retesting under controlled conditions\n"
            
            # Performance rankings
            if reliable_results:
                sorted_by_ops = sorted(reliable_results, key=lambda x: x['ops_per_sec'], reverse=True)
                
                report += f"\n### Performance Rankings (Reliable Measurements Only)\n\n"
                for i, result in enumerate(sorted_by_ops[:5]):
                    mode = "TLS" if result.get('tls', False) else "Non-TLS"
                    quality = result.get('measurement_quality', 'unknown')
                    quality_icon = {'excellent': '🟢', 'good': '🟡', 'fair': '🟠', 'poor': '🔴'}.get(quality, '⚪')
                    cv = (result.get('ops_per_sec_cv', 0) * 100)
                    
                    report += f"{i+1}. **{result['database']} ({mode})**: {result['ops_per_sec']:.0f} ops/sec "
                    report += f"({quality_icon} {quality}, CV: {cv:.1f}%)\n"
            
            # TLS vs Non-TLS comparison if applicable
            if has_tls_data:
                report += f"\n### TLS Performance Impact\n\n"
                
                for db in ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']:
                    tls_results = [r for r in all_results if r['database'] == db and r.get('tls', False)]
                    non_tls_results = [r for r in all_results if r['database'] == db and not r.get('tls', False)]
                    
                    if tls_results and non_tls_results:
                        tls_ops = tls_results[0]['ops_per_sec']
                        non_tls_ops = non_tls_results[0]['ops_per_sec']
                        impact = ((non_tls_ops - tls_ops) / non_tls_ops) * 100
                        
                        # Check if difference is significant based on confidence intervals
                        tls_ci = tls_results[0].get('ops_per_sec_confidence_interval_95', {})
                        non_tls_ci = non_tls_results[0].get('ops_per_sec_confidence_interval_95', {})
                        
                        significant = ""
                        if tls_ci.get('upper', 0) < non_tls_ci.get('lower', 0):
                            significant = " (statistically significant)"
                        elif abs(impact) < 5:
                            significant = " (minimal impact)"
                        
                        report += f"- **{db}**: {impact:+.1f}% performance impact with TLS{significant}\n"
                        report += f"  - Non-TLS: {non_tls_ops:.0f} ± {non_tls_results[0].get('ops_per_sec_stddev', 0):.0f} ops/sec\n"
                        report += f"  - TLS: {tls_ops:.0f} ± {tls_results[0].get('ops_per_sec_stddev', 0):.0f} ops/sec\n"
            
            # WordPress-specific analysis
            report += f"\n### WordPress Performance Estimates\n\n"
            if reliable_results:
                best_result = max(reliable_results, key=lambda x: x['ops_per_sec'])
                best_ops = best_result['ops_per_sec']
                best_db = best_result['database']
                best_mode = "TLS" if best_result.get('tls', False) else "Non-TLS"
                
                # Estimate concurrent users and page loads
                light_pages_per_sec = best_ops / 10   # 10 cache ops per light page
                heavy_pages_per_sec = best_ops / 50   # 50 cache ops per heavy page
                concurrent_users = best_ops / 30      # 30 cache ops per user per second
                
                report += f"**Best Performer:** {best_db} ({best_mode}) - {best_ops:.0f} ops/sec\n\n"
                report += f"**Estimated WordPress Capacity:**\n"
                report += f"- Light pages: ~{light_pages_per_sec:.0f} pages/sec\n"
                report += f"- Heavy pages: ~{heavy_pages_per_sec:.0f} pages/sec\n" 
                report += f"- Concurrent users: ~{concurrent_users:.0f} users (30 ops/user/sec)\n"
                report += f"- Daily page views: ~{light_pages_per_sec * 86400:.0f} (light pages)\n\n"
        
        # Raw data summary if available
        if raw_data:
            report += f"\n## Raw Data Analysis\n\n"
            report += f"Raw iteration data is available for detailed analysis.\n"
            report += f"Files generated:\n"
            report += f"- Individual iteration charts showing consistency\n"
            report += f"- Coefficient of variation analysis\n"
            report += f"- Statistical confidence intervals\n\n"
        
        # Recommendations
        report += f"\n## Recommendations\n\n"
        
        if reliable_results:
            best_db = max(reliable_results, key=lambda x: x['ops_per_sec'])['database']
            report += f"1. **Database Selection:** {best_db} shows the best performance for WordPress workloads\n"
        
        unreliable_count = len([r for r in all_results if r.get('measurement_quality', 'poor') == 'poor'])
        if unreliable_count > 0:
            report += f"2. **Testing Environment:** {unreliable_count} measurements showed high variability - consider:\n"
            report += f"   - Running tests during low system load\n"
            report += f"   - Increasing iteration count for better statistical power\n"
            report += f"   - Checking for background processes affecting performance\n"
        
        report += f"3. **Production Deployment:** Use these results as baseline for capacity planning\n"
        report += f"4. **Monitoring:** Implement performance monitoring to validate production results\n"
        
        # File output
        output_file = self.output_dir / "php_redis_enhanced_benchmark_summary.md"
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Generated: {output_file}")

    def _average_results(self, results_list):
        """Helper: Average multiple results"""
        if len(results_list) == 1:
            return results_list[0]
        
        # Simple averaging for demonstration
        avg_result = results_list[0].copy()
        numeric_fields = ['ops_per_sec', 'avg_latency', 'p95_latency', 'p99_latency', 'error_rate']
        
        for field in numeric_fields:
            values = [r.get(field, 0) for r in results_list if field in r]
            if values:
                avg_result[field] = sum(values) / len(values)
        
        return avg_result

    def generate_all_charts(self):
        """Generate all enhanced charts and reports"""
        print("Loading test results with statistical analysis...")
        results, metadata, raw_data = self.load_test_results()
        
        if not results:
            print("No results found to generate charts")
            return
        
        # Check overall statistics
        total_results = sum(len(test_data) for test_data in results.values())
        reliable_results = sum(1 for test_data in results.values() 
                             for result in test_data 
                             if result.get('measurement_quality', 'poor') != 'poor')
        
        iterations = 1
        if metadata:
            first_test = next(iter(metadata.values()))
            iterations = first_test.get('test_methodology', {}).get('iterations_per_test', 1)
        
        print(f"Generating enhanced charts for {len(results)} test types...")
        print(f"Total measurements: {total_results}")
        print(f"Reliable measurements: {reliable_results}/{total_results}")
        print(f"Iterations per test: {iterations}")
        print(f"Raw data available: {'Yes' if raw_data else 'No'}")
        
        # Generate all chart types
        self.create_statistical_performance_chart(results, metadata)
        self.create_measurement_reliability_chart(results, metadata)
        self.create_confidence_interval_chart(results, metadata)
        
        if raw_data:
            self.create_iteration_variance_chart(raw_data)
        
        self.create_enhanced_summary_report(results, metadata, raw_data)
        
        print(f"\nAll enhanced charts and reports generated in {self.output_dir}")
        
        # Print summary of generated files
        png_files = list(self.output_dir.glob("*.png"))
        md_files = list(self.output_dir.glob("*.md"))
        
        print(f"\nGenerated files:")
        print(f"  📊 Charts: {len(png_files)} PNG files")
        print(f"  📄 Reports: {len(md_files)} Markdown files")
        print(f"  📈 Statistical Analysis: Enhanced with {iterations}-run methodology")
        
        if reliable_results < total_results:
            print(f"  ⚠️  Note: {total_results - reliable_results} measurements showed high variability")
            print(f"     Consider reviewing test conditions for improved reliability")

def main():
    parser = argparse.ArgumentParser(description='Generate enhanced statistical charts from PHP Redis benchmark results')
    parser.add_argument('--results-dir', default='php_benchmark_results', 
                       help='Directory containing JSON result files')
    parser.add_argument('--output-dir', default='php_benchmark_charts', 
                       help='Output directory for charts and reports')
    
    args = parser.parse_args()
    
    # Create generator and run
    generator = EnhancedPHPRedisChartsGenerator(args.results_dir, args.output_dir)
    generator.generate_all_charts()

if __name__ == "__main__":
    main()