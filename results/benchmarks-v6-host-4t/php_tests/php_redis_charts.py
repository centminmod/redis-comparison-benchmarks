#!/usr/bin/env python3
"""
Enhanced PHP Redis Benchmark Charts Generator
Creates comprehensive charts from PHP-based WordPress Redis test results
Compatible with enhanced RedisTestBase.php output format
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

class PHPRedisChartsGenerator:
    def __init__(self, results_dir, output_dir):
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up plotting style
        plt.style.use('default')
        self.colors = {
            'Redis': '#E74C3C',
            'KeyDB': '#27AE60', 
            'Dragonfly': '#F39C12',
            'Valkey': '#8E44AD'
        }
        
        # Chart configuration
        self.dpi = 300
        self.bbox_inches = 'tight'
        
    def load_test_results(self):
        """Load all JSON test results with enhanced metadata handling"""
        results = {}
        metadata = {}
        
        print(f"Loading results from {self.results_dir}...")
        
        json_files = list(self.results_dir.glob("*.json"))
        if not json_files:
            print(f"No JSON files found in {self.results_dir}")
            return {}, {}
            
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                test_name = data.get('test_name', 'Unknown Test')
                
                # Handle both old and new JSON format
                if 'results' in data:
                    # New enhanced format
                    if test_name not in results:
                        results[test_name] = []
                    results[test_name].extend(data['results'])
                    
                    # Store metadata
                    metadata[test_name] = {
                        'timestamp': data.get('timestamp'),
                        'php_version': data.get('php_version'),
                        'test_configuration': data.get('test_configuration', {}),
                        'results_count': data.get('results_count', len(data['results']))
                    }
                else:
                    # Legacy format - treat entire data as results
                    if test_name not in results:
                        results[test_name] = []
                    if isinstance(data, list):
                        results[test_name].extend(data)
                    else:
                        results[test_name].append(data)
                        
                print(f"Loaded {len(data.get('results', [data]))} results from {json_file.name}")
                
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue
        
        print(f"Total test types loaded: {len(results)}")
        for test_name, test_results in results.items():
            print(f"  {test_name}: {len(test_results)} results")
            
        return results, metadata

    def create_performance_comparison_chart(self, results, metadata):
        """Enhanced performance comparison chart with metadata"""
        if not results:
            print("No results to chart")
            return
            
        # Calculate subplot dimensions
        test_count = len(results)
        if test_count == 1:
            fig_size = (12, 8)
            subplot_dims = (1, 1)
        elif test_count <= 4:
            fig_size = (20, 12)
            subplot_dims = (2, 2)
        else:
            fig_size = (24, 16)
            subplot_dims = (3, 2)
            
        fig, axes = plt.subplots(*subplot_dims, figsize=fig_size)
        if test_count == 1:
            axes = [axes]
        elif test_count <= 4:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
            
        # Get overall metadata for title
        first_test = next(iter(metadata.values())) if metadata else {}
        php_version = first_test.get('php_version', 'Unknown')
        test_timestamp = first_test.get('timestamp', '')
        
        fig.suptitle(f'WordPress Redis Tests - Performance Comparison\nPHP {php_version} - {test_timestamp[:10]}', 
                    fontsize=16, fontweight='bold')
        
        databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
        
        for i, (test_name, test_data) in enumerate(results.items()):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            # Separate TLS and non-TLS results
            non_tls_data = [r for r in test_data if not r.get('tls', False)]
            tls_data = [r for r in test_data if r.get('tls', False)]
            
            x = np.arange(len(databases))
            width = 0.35
            
            non_tls_ops = []
            tls_ops = []
            
            for db in databases:
                non_tls_result = next((r for r in non_tls_data if r['database'] == db), None)
                tls_result = next((r for r in tls_data if r['database'] == db), None)
                
                non_tls_ops.append(non_tls_result['ops_per_sec'] if non_tls_result else 0)
                tls_ops.append(tls_result['ops_per_sec'] if tls_result else 0)
            
            bars1 = ax.bar(x - width/2, non_tls_ops, width, label='Non-TLS', alpha=0.8, color='lightblue')
            bars2 = ax.bar(x + width/2, tls_ops, width, label='TLS', alpha=0.8, color='lightcoral')
            
            # Enhanced title with test metadata
            test_meta = metadata.get(test_name, {})
            config = test_meta.get('test_configuration', {})
            flush_status = config.get('flush_before_test', False)
            title = test_name.replace('WordPress ', '')
            if flush_status:
                title += ' (DB Flushed)'
                
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_ylabel('Operations/sec')
            ax.set_xticks(x)
            ax.set_xticklabels(databases, rotation=45)
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.annotate(f'{int(height)}',
                                  xy=(bar.get_x() + bar.get_width() / 2, height),
                                  xytext=(0, 3),
                                  textcoords="offset points",
                                  ha='center', va='bottom', fontsize=8)
        
        # Hide unused subplots
        for i in range(test_count, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_performance_comparison.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
        plt.close()
        print(f"Generated: {output_file}")

    def create_latency_comparison_chart(self, results, metadata):
        """Enhanced latency comparison with error handling"""
        if not results:
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Get metadata for title
        first_test = next(iter(metadata.values())) if metadata else {}
        php_version = first_test.get('php_version', 'Unknown')
        
        fig.suptitle(f'WordPress Redis Tests - Latency Comparison (PHP {php_version})', 
                    fontsize=16, fontweight='bold')
        
        databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
        
        # Collect latency data
        all_avg_latencies = {db: {'non_tls': [], 'tls': []} for db in databases}
        all_p99_latencies = {db: {'non_tls': [], 'tls': []} for db in databases}
        
        for test_name, test_data in results.items():
            for result in test_data:
                db = result['database']
                if db not in databases:
                    continue
                    
                tls_type = 'tls' if result.get('tls', False) else 'non_tls'
                
                if 'avg_latency' in result and result['avg_latency'] > 0:
                    all_avg_latencies[db][tls_type].append(result['avg_latency'])
                if 'p99_latency' in result and result['p99_latency'] > 0:
                    all_p99_latencies[db][tls_type].append(result['p99_latency'])
        
        # Plot average latencies
        x = np.arange(len(databases))
        width = 0.35
        
        avg_non_tls = [np.mean(all_avg_latencies[db]['non_tls']) if all_avg_latencies[db]['non_tls'] else 0 for db in databases]
        avg_tls = [np.mean(all_avg_latencies[db]['tls']) if all_avg_latencies[db]['tls'] else 0 for db in databases]
        
        bars1 = ax1.bar(x - width/2, avg_non_tls, width, label='Non-TLS', alpha=0.8, color='lightblue')
        bars2 = ax1.bar(x + width/2, avg_tls, width, label='TLS', alpha=0.8, color='lightcoral')
        
        ax1.set_title('Average Latency (ms)')
        ax1.set_ylabel('Latency (ms)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(databases)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.annotate(f'{height:.2f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)
        
        # Plot p99 latencies
        p99_non_tls = [np.mean(all_p99_latencies[db]['non_tls']) if all_p99_latencies[db]['non_tls'] else 0 for db in databases]
        p99_tls = [np.mean(all_p99_latencies[db]['tls']) if all_p99_latencies[db]['tls'] else 0 for db in databases]
        
        bars3 = ax2.bar(x - width/2, p99_non_tls, width, label='Non-TLS', alpha=0.8, color='lightblue')
        bars4 = ax2.bar(x + width/2, p99_tls, width, label='TLS', alpha=0.8, color='lightcoral')
        
        ax2.set_title('P99 Latency (ms)')
        ax2.set_ylabel('Latency (ms)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(databases)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax2.annotate(f'{height:.2f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_latency_comparison.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
        plt.close()
        print(f"Generated: {output_file}")

    def create_database_state_chart(self, results, metadata):
        """NEW: Chart showing database state changes (key counts)"""
        if not results:
            return
            
        # Check if we have key count data
        has_key_data = False
        for test_data in results.values():
            for result in test_data:
                if 'initial_key_count' in result or 'final_key_count' in result:
                    has_key_data = True
                    break
            if has_key_data:
                break
                
        if not has_key_data:
            print("No key count data found, skipping database state chart")
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Get metadata for title
        first_test = next(iter(metadata.values())) if metadata else {}
        flush_enabled = first_test.get('test_configuration', {}).get('flush_before_test', False)
        
        fig.suptitle(f'Database State Analysis (Flush: {"Enabled" if flush_enabled else "Disabled"})', 
                    fontsize=16, fontweight='bold')
        
        databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
        
        # Collect key count data
        initial_counts = {db: [] for db in databases}
        final_counts = {db: [] for db in databases}
        key_growth = {db: [] for db in databases}
        
        for test_name, test_data in results.items():
            for result in test_data:
                db = result['database']
                if db not in databases:
                    continue
                    
                initial = result.get('initial_key_count', 0)
                final = result.get('final_key_count', 0)
                
                initial_counts[db].append(initial)
                final_counts[db].append(final)
                key_growth[db].append(final - initial)
        
        # Chart 1: Average key counts
        x = np.arange(len(databases))
        width = 0.35
        
        avg_initial = [np.mean(initial_counts[db]) if initial_counts[db] else 0 for db in databases]
        avg_final = [np.mean(final_counts[db]) if final_counts[db] else 0 for db in databases]
        
        bars1 = ax1.bar(x - width/2, avg_initial, width, label='Initial Keys', alpha=0.8, color='lightgray')
        bars2 = ax1.bar(x + width/2, avg_final, width, label='Final Keys', alpha=0.8, color='lightgreen')
        
        ax1.set_title('Average Key Counts')
        ax1.set_ylabel('Number of Keys')
        ax1.set_xticks(x)
        ax1.set_xticklabels(databases)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)
        
        # Chart 2: Key growth during tests
        avg_growth = [np.mean(key_growth[db]) if key_growth[db] else 0 for db in databases]
        
        bars3 = ax2.bar(databases, avg_growth, alpha=0.8, color='orange')
        
        ax2.set_title('Average Key Growth During Tests')
        ax2.set_ylabel('Keys Added')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars3:
            height = bar.get_height()
            ax2.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_database_state.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
        plt.close()
        print(f"Generated: {output_file}")

    def create_test_specific_charts(self, results, metadata):
        """Enhanced test-specific charts with metadata"""
        for test_name, test_data in results.items():
            if not test_data:
                continue
                
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            
            # Get test metadata
            test_meta = metadata.get(test_name, {})
            config = test_meta.get('test_configuration', {})
            flush_status = config.get('flush_before_test', False)
            php_version = test_meta.get('php_version', 'Unknown')
            
            fig.suptitle(f'{test_name} - Detailed Results\nPHP {php_version} | Flush: {"Yes" if flush_status else "No"}', 
                        fontsize=16, fontweight='bold')
            
            databases = ['Redis', 'KeyDB', 'Dragonfly', 'Valkey']
            
            # Separate TLS and non-TLS data
            non_tls_data = [r for r in test_data if not r.get('tls', False)]
            tls_data = [r for r in test_data if r.get('tls', False)]
            
            # Ops/sec comparison
            ax1 = axes[0, 0]
            non_tls_ops = [next((r['ops_per_sec'] for r in non_tls_data if r['database'] == db), 0) for db in databases]
            tls_ops = [next((r['ops_per_sec'] for r in tls_data if r['database'] == db), 0) for db in databases]
            
            x = np.arange(len(databases))
            width = 0.35
            ax1.bar(x - width/2, non_tls_ops, width, label='Non-TLS', alpha=0.8)
            ax1.bar(x + width/2, tls_ops, width, label='TLS', alpha=0.6)
            ax1.set_title('Operations per Second')
            ax1.set_ylabel('Ops/sec')
            ax1.set_xticks(x)
            ax1.set_xticklabels(databases)
            ax1.legend()
            ax1.grid(axis='y', alpha=0.3)
            
            # Latency comparison
            ax2 = axes[0, 1]
            non_tls_lat = [next((r.get('avg_latency', 0) for r in non_tls_data if r['database'] == db), 0) for db in databases]
            tls_lat = [next((r.get('avg_latency', 0) for r in tls_data if r['database'] == db), 0) for db in databases]
            
            ax2.bar(x - width/2, non_tls_lat, width, label='Non-TLS', alpha=0.8)
            ax2.bar(x + width/2, tls_lat, width, label='TLS', alpha=0.6)
            ax2.set_title('Average Latency')
            ax2.set_ylabel('Latency (ms)')
            ax2.set_xticks(x)
            ax2.set_xticklabels(databases)
            ax2.legend()
            ax2.grid(axis='y', alpha=0.3)
            
            # Error rate comparison
            ax3 = axes[1, 0]
            non_tls_err = [next((r.get('error_rate', 0) for r in non_tls_data if r['database'] == db), 0) for db in databases]
            tls_err = [next((r.get('error_rate', 0) for r in tls_data if r['database'] == db), 0) for db in databases]
            
            ax3.bar(x - width/2, non_tls_err, width, label='Non-TLS', alpha=0.8)
            ax3.bar(x + width/2, tls_err, width, label='TLS', alpha=0.6)
            ax3.set_title('Error Rate')
            ax3.set_ylabel('Error Rate (%)')
            ax3.set_xticks(x)
            ax3.set_xticklabels(databases)
            ax3.legend()
            ax3.grid(axis='y', alpha=0.3)
            
            # Key growth analysis (NEW)
            ax4 = axes[1, 1]
            if any('final_key_count' in r for r in test_data):
                key_growth = []
                for db in databases:
                    db_results = [r for r in test_data if r['database'] == db]
                    if db_results:
                        avg_growth = np.mean([r.get('final_key_count', 0) - r.get('initial_key_count', 0) 
                                            for r in db_results])
                        key_growth.append(avg_growth)
                    else:
                        key_growth.append(0)
                
                ax4.bar(databases, key_growth, alpha=0.8, color='green')
                ax4.set_title('Average Key Growth')
                ax4.set_ylabel('Keys Added')
                ax4.grid(axis='y', alpha=0.3)
                
                # Add value labels
                for i, height in enumerate(key_growth):
                    if height != 0:
                        ax4.annotate(f'{int(height)}',
                                   xy=(i, height),
                                   xytext=(0, 3),
                                   textcoords="offset points",
                                   ha='center', va='bottom', fontsize=8)
            else:
                ax4.text(0.5, 0.5, 'No key count data available', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Key Growth Data')
            
            plt.tight_layout()
            test_slug = test_name.lower().replace(' ', '_').replace('wordpress', 'wp')
            output_file = self.output_dir / f'{test_slug}_detailed.png'
            plt.savefig(output_file, dpi=self.dpi, bbox_inches=self.bbox_inches)
            plt.close()
            print(f"Generated: {output_file}")

    def create_summary_report(self, results, metadata):
        """Enhanced summary report with metadata and analysis"""
        if not results:
            print("No results to summarize")
            return
            
        # Get overall metadata
        first_test = next(iter(metadata.values())) if metadata else {}
        php_version = first_test.get('php_version', 'Unknown')
        test_config = first_test.get('test_configuration', {})
        
        report = f"# WordPress Redis Benchmark Results\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**PHP Version:** {php_version}\n"
        report += f"**Test Configuration:**\n"
        report += f"- Flush Before Test: {'Yes' if test_config.get('flush_before_test') else 'No'}\n"
        report += f"- TLS Testing: {'Yes' if test_config.get('test_tls') else 'No'}\n\n"
        
        # Performance summary table
        report += "## Performance Summary\n\n"
        report += "| Test | Database | Mode | Ops/sec | Avg Latency (ms) | P99 Latency (ms) | Error Rate (%) | Key Growth |\n"
        report += "|------|----------|------|---------|------------------|------------------|----------------|------------|\n"
        
        for test_name, test_data in results.items():
            for result in test_data:
                mode = "TLS" if result.get('tls', False) else "Non-TLS"
                key_growth = result.get('final_key_count', 0) - result.get('initial_key_count', 0)
                
                report += f"| {test_name.replace('WordPress ', '')} | {result['database']} | {mode} | "
                report += f"{result['ops_per_sec']:.2f} | {result.get('avg_latency', 0):.2f} | "
                report += f"{result.get('p99_latency', 0):.2f} | {result.get('error_rate', 0):.2f} | {key_growth} |\n"
        
        # Top performers analysis
        report += "\n## Performance Analysis\n\n"
        
        all_results = []
        for test_data in results.values():
            all_results.extend(test_data)
        
        if all_results:
            # Sort by ops/sec
            sorted_by_ops = sorted(all_results, key=lambda x: x['ops_per_sec'], reverse=True)
            
            report += "### Highest Throughput (Top 5)\n\n"
            for i, result in enumerate(sorted_by_ops[:5]):
                mode = "TLS" if result.get('tls', False) else "Non-TLS"
                report += f"{i+1}. **{result['database']} ({mode})**: {result['ops_per_sec']:.2f} ops/sec\n"
            
            # Sort by latency (lowest first)
            sorted_by_latency = sorted([r for r in all_results if r.get('avg_latency', 0) > 0], 
                                     key=lambda x: x.get('avg_latency', float('inf')))
            
            if sorted_by_latency:
                report += "\n### Lowest Latency (Top 5)\n\n"
                for i, result in enumerate(sorted_by_latency[:5]):
                    mode = "TLS" if result.get('tls', False) else "Non-TLS"
                    report += f"{i+1}. **{result['database']} ({mode})**: {result.get('avg_latency', 0):.2f} ms\n"
            
            # Database state analysis
            if any('initial_key_count' in r for r in all_results):
                report += "\n### Database State Analysis\n\n"
                
                flush_results = [r for r in all_results if r.get('flushed_before_test', False)]
                no_flush_results = [r for r in all_results if not r.get('flushed_before_test', False)]
                
                if flush_results:
                    avg_growth_flush = np.mean([r.get('final_key_count', 0) - r.get('initial_key_count', 0) 
                                              for r in flush_results])
                    report += f"- Average key growth (with flush): {avg_growth_flush:.1f} keys\n"
                
                if no_flush_results:
                    avg_growth_no_flush = np.mean([r.get('final_key_count', 0) - r.get('initial_key_count', 0) 
                                                 for r in no_flush_results])
                    report += f"- Average key growth (without flush): {avg_growth_no_flush:.1f} keys\n"
        
        # Test metadata
        report += "\n## Test Metadata\n\n"
        for test_name, meta in metadata.items():
            report += f"### {test_name}\n"
            report += f"- Results Count: {meta.get('results_count', 'Unknown')}\n"
            report += f"- Timestamp: {meta.get('timestamp', 'Unknown')}\n"
            if meta.get('test_configuration'):
                config = meta['test_configuration']
                report += f"- Configuration: {config}\n"
            report += "\n"
        
        output_file = self.output_dir / "php_redis_benchmark_summary.md"
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Generated: {output_file}")

    def generate_all_charts(self):
        """Generate all charts and reports"""
        print("Loading test results...")
        results, metadata = self.load_test_results()
        
        if not results:
            print("No results found to generate charts")
            return
        
        print(f"Generating charts for {len(results)} test types...")
        
        # Generate all chart types
        self.create_performance_comparison_chart(results, metadata)
        self.create_latency_comparison_chart(results, metadata)
        self.create_database_state_chart(results, metadata)
        self.create_test_specific_charts(results, metadata)
        self.create_summary_report(results, metadata)
        
        print(f"All charts and reports generated in {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Generate enhanced charts from PHP Redis benchmark results')
    parser.add_argument('--results-dir', default='php_benchmark_results', 
                       help='Directory containing JSON result files')
    parser.add_argument('--output-dir', default='php_benchmark_charts', 
                       help='Output directory for charts and reports')
    
    args = parser.parse_args()
    
    # Create generator and run
    generator = PHPRedisChartsGenerator(args.results_dir, args.output_dir)
    generator.generate_all_charts()

if __name__ == "__main__":
    main()