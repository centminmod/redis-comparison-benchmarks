#!/usr/bin/env python3
"""
Enhanced PHP Redis Implementation Comparison Chart Generator

This script generates comprehensive charts comparing phpredis and Predis implementations
with focus on TLS reliability, performance characteristics, and statistical analysis.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse
import os
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class PHPRedisComparisonCharts:
    def __init__(self, results_dir, output_dir):
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced styling
        plt.style.use('seaborn-v0_8')
        self.colors = {
            'phpredis': '#E74C3C',      # Red
            'predis': '#3498DB',        # Blue
            'tls': '#F39C12',           # Orange
            'non_tls': '#27AE60',       # Green
            'excellent': '#2ECC71',      # Light green
            'good': '#F1C40F',          # Yellow
            'fair': '#E67E22',          # Orange
            'poor': '#E74C3C'           # Red
        }
        
        self.data = None
        self.comparison_data = None
        
    def load_data(self):
        """Load data from both phpredis and Predis result files"""
        data = []
        
        # Find JSON files
        json_files = list(self.results_dir.glob('*.json'))
        
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in {self.results_dir}")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    file_data = json.load(f)
                
                # Determine implementation from filename or content
                implementation = 'unknown'
                if 'predis' in json_file.name.lower():
                    implementation = 'predis'
                elif 'phpredis' in json_file.name.lower() or 'redis_extension' in str(file_data):
                    implementation = 'phpredis'
                elif 'redis_implementation' in file_data:
                    implementation = file_data['redis_implementation']
                elif 'predis_version' in file_data:
                    implementation = 'predis'
                elif 'redis_extension_version' in file_data:
                    implementation = 'phpredis'
                
                # Process results
                if 'results' in file_data:
                    for result in file_data['results']:
                        result['implementation'] = implementation
                        result['source_file'] = json_file.name
                        data.append(result)
                        
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue
        
        if not data:
            raise ValueError("No valid data found in JSON files")
        
        self.data = pd.DataFrame(data)
        print(f"Loaded {len(self.data)} results from {len(json_files)} files")
        print(f"Implementations found: {self.data['implementation'].unique()}")
        
        return self.data
    
    def prepare_comparison_data(self):
        """Prepare data for implementation comparison"""
        if self.data is None:
            self.load_data()
        
        # Create comparison dataset
        comparison_rows = []
        
        for database in self.data['database'].unique():
            for tls in [True, False]:
                db_tls_data = self.data[
                    (self.data['database'] == database) & 
                    (self.data['tls'] == tls)
                ]
                
                if len(db_tls_data) == 0:
                    continue
                
                # Group by implementation
                for impl in db_tls_data['implementation'].unique():
                    impl_data = db_tls_data[db_tls_data['implementation'] == impl]
                    
                    if len(impl_data) > 0:
                        row = impl_data.iloc[0].copy()
                        row['comparison_key'] = f"{database}_{'TLS' if tls else 'nonTLS'}"
                        comparison_rows.append(row)
        
        self.comparison_data = pd.DataFrame(comparison_rows)
        return self.comparison_data
    
    def create_implementation_performance_comparison(self):
        """Create side-by-side performance comparison chart"""
        if self.comparison_data is None:
            self.prepare_comparison_data()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('PHP Redis Implementation Performance Comparison', fontsize=16, fontweight='bold')
        
        # 1. Operations per second comparison
        ops_data = self.comparison_data.pivot_table(
            index='comparison_key', 
            columns='implementation', 
            values='ops_per_sec', 
            aggfunc='mean'
        ).fillna(0)
        
        ops_data.plot(kind='bar', ax=ax1, color=[self.colors['phpredis'], self.colors['predis']])
        ax1.set_title('Operations per Second', fontweight='bold')
        ax1.set_ylabel('Ops/sec')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(title='Implementation')
        
        # 2. Average latency comparison
        latency_data = self.comparison_data.pivot_table(
            index='comparison_key', 
            columns='implementation', 
            values='avg_latency', 
            aggfunc='mean'
        ).fillna(0)
        
        latency_data.plot(kind='bar', ax=ax2, color=[self.colors['phpredis'], self.colors['predis']])
        ax2.set_title('Average Latency', fontweight='bold')
        ax2.set_ylabel('Latency (ms)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title='Implementation')
        
        # 3. TLS vs Non-TLS performance impact
        tls_comparison = []
        for impl in self.comparison_data['implementation'].unique():
            impl_data = self.comparison_data[self.comparison_data['implementation'] == impl]
            
            for db in impl_data['database'].unique():
                db_data = impl_data[impl_data['database'] == db]
                tls_data = db_data[db_data['tls'] == True]
                non_tls_data = db_data[db_data['tls'] == False]
                
                if len(tls_data) > 0 and len(non_tls_data) > 0:
                    tls_ops = tls_data['ops_per_sec'].iloc[0]
                    non_tls_ops = non_tls_data['ops_per_sec'].iloc[0]
                    
                    if non_tls_ops > 0:
                        impact = ((non_tls_ops - tls_ops) / non_tls_ops) * 100
                        tls_comparison.append({
                            'database': db,
                            'implementation': impl,
                            'tls_impact_percent': impact
                        })
        
        if tls_comparison:
            tls_df = pd.DataFrame(tls_comparison)
            tls_pivot = tls_df.pivot(index='database', columns='implementation', values='tls_impact_percent')
            
            tls_pivot.plot(kind='bar', ax=ax3, color=[self.colors['phpredis'], self.colors['predis']])
            ax3.set_title('TLS Performance Impact (%)', fontweight='bold')
            ax3.set_ylabel('Performance Impact (%)')
            ax3.tick_params(axis='x', rotation=45)
            ax3.legend(title='Implementation')
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # 4. Measurement quality comparison
        quality_mapping = {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1, 'unknown': 0}
        self.comparison_data['quality_score'] = self.comparison_data['measurement_quality'].map(quality_mapping)
        
        quality_data = self.comparison_data.pivot_table(
            index='comparison_key', 
            columns='implementation', 
            values='quality_score', 
            aggfunc='mean'
        ).fillna(0)
        
        quality_data.plot(kind='bar', ax=ax4, color=[self.colors['phpredis'], self.colors['predis']])
        ax4.set_title('Measurement Quality Score', fontweight='bold')
        ax4.set_ylabel('Quality Score (4=Excellent, 1=Poor)')
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend(title='Implementation')
        ax4.set_ylim(0, 4.5)
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_implementation_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved implementation comparison chart: {output_file}")
        plt.close()
    
    def create_tls_reliability_analysis(self):
        """Create TLS reliability comparison chart"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('TLS Reliability Analysis: phpredis vs Predis', fontsize=16, fontweight='bold')
        
        # 1. TLS Success Rate by Implementation
        tls_data = self.comparison_data[self.comparison_data['tls'] == True]
        
        if len(tls_data) > 0:
            # Count successful TLS connections by implementation
            tls_success = tls_data.groupby(['implementation', 'database']).size().unstack(fill_value=0)
            total_databases = len(self.comparison_data['database'].unique())
            
            tls_success_rate = (tls_success > 0).sum(axis=1) / total_databases * 100
            
            bars = ax1.bar(tls_success_rate.index, tls_success_rate.values, 
                          color=[self.colors[impl] for impl in tls_success_rate.index])
            ax1.set_title('TLS Connection Success Rate', fontweight='bold')
            ax1.set_ylabel('Success Rate (%)')
            ax1.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar, value in zip(bars, tls_success_rate.values):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                        f'{value:.1f}%', ha='center', va='bottom')
        
        # 2. TLS vs Non-TLS Latency Distribution
        if len(self.comparison_data) > 0:
            for impl in self.comparison_data['implementation'].unique():
                impl_data = self.comparison_data[self.comparison_data['implementation'] == impl]
                
                tls_latencies = impl_data[impl_data['tls'] == True]['avg_latency']
                non_tls_latencies = impl_data[impl_data['tls'] == False]['avg_latency']
                
                if len(tls_latencies) > 0:
                    ax2.scatter(tls_latencies, [impl + '_TLS'] * len(tls_latencies), 
                              color=self.colors['tls'], alpha=0.7, s=60)
                if len(non_tls_latencies) > 0:
                    ax2.scatter(non_tls_latencies, [impl + '_NonTLS'] * len(non_tls_latencies), 
                              color=self.colors['non_tls'], alpha=0.7, s=60)
            
            ax2.set_title('Latency Distribution: TLS vs Non-TLS', fontweight='bold')
            ax2.set_xlabel('Latency (ms)')
            ax2.grid(True, alpha=0.3)
        
        # 3. Implementation Reliability Heatmap
        reliability_matrix = []
        databases = sorted(self.comparison_data['database'].unique())
        implementations = sorted(self.comparison_data['implementation'].unique())
        
        for impl in implementations:
            row = []
            for db in databases:
                # TLS success indicator
                tls_success = len(self.comparison_data[
                    (self.comparison_data['implementation'] == impl) & 
                    (self.comparison_data['database'] == db) & 
                    (self.comparison_data['tls'] == True)
                ]) > 0
                row.append(1 if tls_success else 0)
            reliability_matrix.append(row)
        
        sns.heatmap(reliability_matrix, annot=True, cmap='RdYlGn', 
                   xticklabels=databases, yticklabels=implementations,
                   ax=ax3, cbar_kws={'label': 'TLS Success (1=Yes, 0=No)'})
        ax3.set_title('TLS Success Matrix', fontweight='bold')
        
        # 4. Performance vs Reliability Trade-off
        if len(tls_data) > 0:
            # Calculate reliability score and performance for each implementation
            trade_off_data = []
            
            for impl in self.comparison_data['implementation'].unique():
                impl_data = self.comparison_data[self.comparison_data['implementation'] == impl]
                
                # Reliability: TLS success rate
                tls_impl_data = impl_data[impl_data['tls'] == True]
                reliability = len(tls_impl_data) / len(databases) * 100 if len(databases) > 0 else 0
                
                # Performance: average ops/sec for non-TLS
                non_tls_impl_data = impl_data[impl_data['tls'] == False]
                performance = non_tls_impl_data['ops_per_sec'].mean() if len(non_tls_impl_data) > 0 else 0
                
                trade_off_data.append({
                    'implementation': impl,
                    'reliability': reliability,
                    'performance': performance
                })
            
            trade_off_df = pd.DataFrame(trade_off_data)
            
            for _, row in trade_off_df.iterrows():
                ax4.scatter(row['performance'], row['reliability'], 
                          color=self.colors[row['implementation']], s=200, alpha=0.7)
                ax4.annotate(row['implementation'], 
                           (row['performance'], row['reliability']),
                           xytext=(5, 5), textcoords='offset points')
            
            ax4.set_title('Performance vs TLS Reliability Trade-off', fontweight='bold')
            ax4.set_xlabel('Performance (ops/sec)')
            ax4.set_ylabel('TLS Reliability (%)')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_tls_reliability_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved TLS reliability analysis: {output_file}")
        plt.close()
    
    def create_statistical_comparison(self):
        """Create statistical analysis comparison charts"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Statistical Analysis: Implementation Comparison', fontsize=16, fontweight='bold')
        
        # 1. Coefficient of Variation comparison
        if 'ops_per_sec_cv' in self.comparison_data.columns:
            cv_data = self.comparison_data.pivot_table(
                index='comparison_key', 
                columns='implementation', 
                values='ops_per_sec_cv', 
                aggfunc='mean'
            ).fillna(0) * 100  # Convert to percentage
            
            cv_data.plot(kind='bar', ax=ax1, color=[self.colors['phpredis'], self.colors['predis']])
            ax1.set_title('Coefficient of Variation (%)', fontweight='bold')
            ax1.set_ylabel('CV (%)')
            ax1.tick_params(axis='x', rotation=45)
            ax1.axhline(y=2, color='green', linestyle='--', alpha=0.7, label='Excellent (<2%)')
            ax1.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Good (<5%)')
            ax1.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Fair (<10%)')
            ax1.legend()
        
        # 2. Error rate comparison
        if 'error_rate' in self.comparison_data.columns:
            error_data = self.comparison_data.pivot_table(
                index='comparison_key', 
                columns='implementation', 
                values='error_rate', 
                aggfunc='mean'
            ).fillna(0)
            
            error_data.plot(kind='bar', ax=ax2, color=[self.colors['phpredis'], self.colors['predis']])
            ax2.set_title('Error Rate (%)', fontweight='bold')
            ax2.set_ylabel('Error Rate (%)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.legend(title='Implementation')
        
        # 3. Confidence interval comparison
        if 'ops_per_sec_confidence_interval_95' in self.comparison_data.columns:
            # Extract confidence interval widths
            ci_widths = []
            for _, row in self.comparison_data.iterrows():
                ci = row.get('ops_per_sec_confidence_interval_95', {})
                if isinstance(ci, dict) and 'upper' in ci and 'lower' in ci:
                    width = ci['upper'] - ci['lower']
                    ci_widths.append({
                        'comparison_key': row['comparison_key'],
                        'implementation': row['implementation'],
                        'ci_width': width
                    })
            
            if ci_widths:
                ci_df = pd.DataFrame(ci_widths)
                ci_pivot = ci_df.pivot_table(
                    index='comparison_key', 
                    columns='implementation', 
                    values='ci_width', 
                    aggfunc='mean'
                ).fillna(0)
                
                ci_pivot.plot(kind='bar', ax=ax3, color=[self.colors['phpredis'], self.colors['predis']])
                ax3.set_title('95% Confidence Interval Width', fontweight='bold')
                ax3.set_ylabel('CI Width (ops/sec)')
                ax3.tick_params(axis='x', rotation=45)
                ax3.legend(title='Implementation')
        
        # 4. Quality distribution
        quality_dist = self.comparison_data.groupby(['implementation', 'measurement_quality']).size().unstack(fill_value=0)
        
        if len(quality_dist) > 0:
            quality_colors = [self.colors['excellent'], self.colors['good'], self.colors['fair'], self.colors['poor']]
            quality_dist.plot(kind='bar', stacked=True, ax=ax4, 
                            color=quality_colors[:len(quality_dist.columns)])
            ax4.set_title('Measurement Quality Distribution', fontweight='bold')
            ax4.set_ylabel('Number of Tests')
            ax4.tick_params(axis='x', rotation=0)
            ax4.legend(title='Quality', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        output_file = self.output_dir / 'php_redis_statistical_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved statistical comparison: {output_file}")
        plt.close()
    
    def create_implementation_summary_report(self):
        """Create a comprehensive summary report"""
        if self.comparison_data is None:
            self.prepare_comparison_data()
        
        report_file = self.output_dir / 'php_redis_implementation_comparison_report.md'
        
        with open(report_file, 'w') as f:
            f.write("# PHP Redis Implementation Comparison Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
            
            # Implementation overview
            implementations = self.comparison_data['implementation'].unique()
            f.write("## Implementation Overview\n\n")
            f.write("| Implementation | Total Tests | TLS Tests | Non-TLS Tests |\n")
            f.write("|---|---|---|---|\n")
            
            for impl in implementations:
                impl_data = self.comparison_data[self.comparison_data['implementation'] == impl]
                total = len(impl_data)
                tls = len(impl_data[impl_data['tls'] == True])
                non_tls = len(impl_data[impl_data['tls'] == False])
                f.write(f"| {impl} | {total} | {tls} | {non_tls} |\n")
            
            # Performance summary
            f.write("\n## Performance Summary\n\n")
            for impl in implementations:
                impl_data = self.comparison_data[self.comparison_data['implementation'] == impl]
                
                if len(impl_data) > 0:
                    avg_ops = impl_data['ops_per_sec'].mean()
                    avg_latency = impl_data['avg_latency'].mean()
                    
                    f.write(f"### {impl}\n")
                    f.write(f"- **Average Operations/sec:** {avg_ops:.0f}\n")
                    f.write(f"- **Average Latency:** {avg_latency:.3f}ms\n")
                    
                    # TLS performance impact
                    tls_data = impl_data[impl_data['tls'] == True]
                    non_tls_data = impl_data[impl_data['tls'] == False]
                    
                    if len(tls_data) > 0 and len(non_tls_data) > 0:
                        tls_ops = tls_data['ops_per_sec'].mean()
                        non_tls_ops = non_tls_data['ops_per_sec'].mean()
                        impact = ((non_tls_ops - tls_ops) / non_tls_ops) * 100
                        f.write(f"- **TLS Performance Impact:** {impact:.1f}%\n")
                    
                    f.write("\n")
            
            # TLS reliability
            f.write("## TLS Reliability\n\n")
            databases = self.comparison_data['database'].unique()
            total_databases = len(databases)
            
            for impl in implementations:
                impl_tls_data = self.comparison_data[
                    (self.comparison_data['implementation'] == impl) & 
                    (self.comparison_data['tls'] == True)
                ]
                tls_success_count = len(impl_tls_data['database'].unique())
                success_rate = (tls_success_count / total_databases) * 100 if total_databases > 0 else 0
                
                f.write(f"- **{impl} TLS Success Rate:** {success_rate:.1f}% ({tls_success_count}/{total_databases} databases)\n")
            
            # Recommendations
            f.write("\n## Recommendations\n\n")
            
            phpredis_data = self.comparison_data[self.comparison_data['implementation'] == 'phpredis']
            predis_data = self.comparison_data[self.comparison_data['implementation'] == 'predis']
            
            if len(phpredis_data) > 0 and len(predis_data) > 0:
                phpredis_avg = phpredis_data['ops_per_sec'].mean()
                predis_avg = predis_data['ops_per_sec'].mean()
                
                phpredis_tls_success = len(phpredis_data[phpredis_data['tls'] == True])
                predis_tls_success = len(predis_data[predis_data['tls'] == True])
                
                f.write("### Performance vs Reliability Trade-offs\n\n")
                
                if phpredis_avg > predis_avg:
                    perf_ratio = phpredis_avg / predis_avg
                    f.write(f"- **phpredis** shows {perf_ratio:.1f}x better performance than Predis\n")
                
                if predis_tls_success > phpredis_tls_success:
                    f.write(f"- **Predis** shows better TLS reliability ({predis_tls_success} vs {phpredis_tls_success} successful connections)\n")
                
                f.write("\n### Use Case Recommendations\n\n")
                f.write("- **High Performance, Non-TLS:** Use phpredis for maximum throughput\n")
                f.write("- **TLS Required:** Use Predis for better SSL reliability\n")
                f.write("- **Cross-Platform Deployment:** Use Predis for consistency\n")
                f.write("- **Extension Dependencies:** Use Predis if phpredis installation is challenging\n")
        
        print(f"Saved implementation comparison report: {report_file}")
    
    def create_separated_tls_comparison(self):
        """Create separate charts for non-TLS and TLS comparisons to handle missing data gracefully"""
        if self.comparison_data is None:
            self.prepare_comparison_data()
        
        # Check what TLS data we have
        non_tls_data = self.comparison_data[self.comparison_data['tls'] == False]
        tls_data = self.comparison_data[self.comparison_data['tls'] == True]
        
        implementations = self.comparison_data['implementation'].unique()
        databases = self.comparison_data['database'].unique()
        
        print(f"Data availability:")
        for impl in implementations:
            non_tls_count = len(non_tls_data[non_tls_data['implementation'] == impl])
            tls_count = len(tls_data[tls_data['implementation'] == impl])
            print(f"  {impl}: {non_tls_count} non-TLS, {tls_count} TLS results")
        
        # Generate Non-TLS comparison chart
        if len(non_tls_data) > 0:
            self._create_single_mode_comparison(non_tls_data, "Non-TLS", "non_tls")
        
        # Generate TLS comparison chart (with missing data handling)
        if len(tls_data) > 0:
            self._create_single_mode_comparison(tls_data, "TLS", "tls")
        else:
            print("⚠️ No TLS data available for comparison charts")
    
    def _create_single_mode_comparison(self, mode_data, mode_name, mode_suffix):
        """Create comparison chart for a specific TLS mode (non-TLS or TLS)"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'PHP Redis Implementation Comparison - {mode_name} Mode', fontsize=16, fontweight='bold')
        
        implementations = mode_data['implementation'].unique()
        databases = mode_data['database'].unique()
        
        # 1. Operations per second comparison
        ops_data = mode_data.pivot_table(
            index='database', 
            columns='implementation', 
            values='ops_per_sec', 
            aggfunc='mean'
        )
        
        # Handle missing implementations
        for impl in ['phpredis', 'predis']:
            if impl not in ops_data.columns:
                ops_data[impl] = np.nan
        
        # Plot with proper missing data handling
        ax1_data = ops_data.fillna(0)  # Fill NaN with 0 for plotting
        bars = ax1_data.plot(kind='bar', ax=ax1, color=[self.colors.get('phpredis', '#999'), self.colors.get('predis', '#999')])
        ax1.set_title(f'Operations per Second - {mode_name}', fontweight='bold')
        ax1.set_ylabel('Ops/sec')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(title='Implementation')
        
        # Add missing data annotations
        for i, db in enumerate(ax1_data.index):
            for j, impl in enumerate(ax1_data.columns):
                if pd.isna(ops_data.loc[db, impl]):
                    ax1.text(i, ax1_data.loc[db, impl] + max(ax1_data.max()) * 0.02, 
                           'No Data', ha='center', va='bottom', fontsize=8, color='red')
        
        # 2. Average latency comparison
        latency_data = mode_data.pivot_table(
            index='database', 
            columns='implementation', 
            values='avg_latency', 
            aggfunc='mean'
        )
        
        for impl in ['phpredis', 'predis']:
            if impl not in latency_data.columns:
                latency_data[impl] = np.nan
        
        ax2_data = latency_data.fillna(0)
        latency_data.fillna(0).plot(kind='bar', ax=ax2, color=[self.colors.get('phpredis', '#999'), self.colors.get('predis', '#999')])
        ax2.set_title(f'Average Latency - {mode_name}', fontweight='bold')
        ax2.set_ylabel('Latency (ms)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title='Implementation')
        
        # Add missing data annotations for latency
        for i, db in enumerate(ax2_data.index):
            for j, impl in enumerate(ax2_data.columns):
                if pd.isna(latency_data.loc[db, impl]):
                    ax2.text(i, ax2_data.loc[db, impl] + max(ax2_data.max()) * 0.02, 
                           'No Data', ha='center', va='bottom', fontsize=8, color='red')
        
        # 3. Quality comparison
        if 'measurement_quality' in mode_data.columns:
            quality_mapping = {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1, 'unknown': 0}
            mode_data_copy = mode_data.copy()
            mode_data_copy['quality_score'] = mode_data_copy['measurement_quality'].map(quality_mapping)
            
            quality_data = mode_data_copy.pivot_table(
                index='database', 
                columns='implementation', 
                values='quality_score', 
                aggfunc='mean'
            )
            
            for impl in ['phpredis', 'predis']:
                if impl not in quality_data.columns:
                    quality_data[impl] = np.nan
            
            quality_data.fillna(0).plot(kind='bar', ax=ax3, color=[self.colors.get('phpredis', '#999'), self.colors.get('predis', '#999')])
            ax3.set_title(f'Measurement Quality - {mode_name}', fontweight='bold')
            ax3.set_ylabel('Quality Score (4=Excellent, 1=Poor)')
            ax3.tick_params(axis='x', rotation=45)
            ax3.legend(title='Implementation')
            ax3.set_ylim(0, 4.5)
        
        # 4. Implementation availability matrix
        availability_matrix = []
        for impl in ['phpredis', 'predis']:
            row = []
            for db in databases:
                has_data = len(mode_data[(mode_data['implementation'] == impl) & (mode_data['database'] == db)]) > 0
                row.append(1 if has_data else 0)
            availability_matrix.append(row)
        
        sns.heatmap(availability_matrix, annot=True, cmap='RdYlGn', 
                   xticklabels=databases, yticklabels=['phpredis', 'predis'],
                   ax=ax4, cbar_kws={'label': 'Data Available (1=Yes, 0=No)'})
        ax4.set_title(f'{mode_name} Data Availability Matrix', fontweight='bold')
        
        plt.tight_layout()
        output_file = self.output_dir / f'php_redis_implementation_comparison_{mode_suffix}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved {mode_name} comparison chart: {output_file}")
        plt.close()

    def generate_all_charts(self):
        """Generate all comparison charts with enhanced missing data handling"""
        print("Loading data...")
        self.load_data()
        
        print("Preparing comparison data...")
        self.prepare_comparison_data()
        
        # Check data availability for better reporting
        non_tls_data = self.comparison_data[self.comparison_data['tls'] == False]
        tls_data = self.comparison_data[self.comparison_data['tls'] == True]
        implementations = self.comparison_data['implementation'].unique()
        
        print(f"\n=== Data Availability Summary ===")
        print(f"Implementations found: {list(implementations)}")
        print(f"Non-TLS results: {len(non_tls_data)} entries")
        print(f"TLS results: {len(tls_data)} entries")
        
        for impl in implementations:
            impl_non_tls = len(non_tls_data[non_tls_data['implementation'] == impl])
            impl_tls = len(tls_data[tls_data['implementation'] == impl])
            print(f"  {impl}: {impl_non_tls} non-TLS, {impl_tls} TLS")
        
        print("\n=== Generating Charts ===")
        
        # Generate original combined comparison (for backward compatibility)
        print("Generating combined implementation performance comparison...")
        self.create_implementation_performance_comparison()
        
        # Generate separated TLS mode comparisons (enhanced)
        print("Generating separated TLS mode comparisons...")
        self.create_separated_tls_comparison()
        
        print("Generating TLS reliability analysis...")
        self.create_tls_reliability_analysis()
        
        print("Generating statistical comparison...")
        self.create_statistical_comparison()
        
        print("Generating summary report...")
        self.create_implementation_summary_report()
        
        print(f"\nAll charts and reports saved to: {self.output_dir}")
        print(f"📊 Chart types generated:")
        print(f"  - Combined comparison (original)")
        print(f"  - Separated non-TLS comparison")
        if len(tls_data) > 0:
            print(f"  - Separated TLS comparison")
        else:
            print(f"  - ⚠️ TLS comparison skipped (no TLS data)")
        print(f"  - TLS reliability analysis")
        print(f"  - Statistical comparison")
        print(f"  - Summary report")

def main():
    parser = argparse.ArgumentParser(description='Generate PHP Redis implementation comparison charts')
    parser.add_argument('--results-dir', required=True, help='Directory containing JSON result files')
    parser.add_argument('--output-dir', required=True, help='Directory to save generated charts')
    parser.add_argument('--compare-implementations', action='store_true', 
                       help='Generate implementation comparison charts')
    
    args = parser.parse_args()
    
    try:
        chart_generator = PHPRedisComparisonCharts(args.results_dir, args.output_dir)
        
        if args.compare_implementations:
            chart_generator.generate_all_charts()
        else:
            # Generate basic charts if no specific comparison requested
            chart_generator.generate_all_charts()
        
        print("✅ Chart generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error generating charts: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()