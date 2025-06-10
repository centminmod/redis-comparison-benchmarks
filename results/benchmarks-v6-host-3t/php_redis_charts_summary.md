# PHP Redis Performance Charts Summary with Technical Analysis

## Overview
This document provides a comprehensive visual analysis of Redis-compatible database performance using both traditional memtier benchmarks and real-world WordPress object cache simulations. Each chart includes technical explanations to help interpret the performance metrics and make informed database selection decisions.

## Chart Color Coding
- **Redis**: Red
- **KeyDB**: Green
- **Dragonfly**: Orange
- **Valkey**: Purple

## Quality Indicators (for PHP charts)
- 🟢 **Excellent** (CV < 2%): Highly reliable measurements
- 🟡 **Good** (CV < 5%): Reliable measurements
- 🟠 **Fair** (CV < 10%): Acceptable measurements
- 🔴 **Poor** (CV ≥ 10%): Less reliable measurements

*CV = Coefficient of Variation (standard deviation / mean × 100%)*

## Test Configuration
- **Thread Variant**: 3
- **Workflow Run**: 40
- **Commit SHA**: 05a9804d3fae10e371d14a17fe08aaa974891052
- **Run Date**: Tue Jun 10 07:39:12 UTC 2025
- **Redis IO Threads**: 3
- **KeyDB Server Threads**: 3
- **Dragonfly Proactor Threads**: 3
- **Valkey IO Threads**: 3

## Section A: Basic Performance Charts

<details>
<summary><strong>📊 Latency Performance Charts</strong></summary>

### Average Latency Charts


#### nonTLS AVG Latency
**Average latency** for Sets, Gets, and Totals operations across thread counts. Shows typical response time performance under different workloads. Lower values indicate better user experience and more responsive database operations.

![nonTLS AVG Latency](latency-nonTLS-avg-single.png)


#### nonTLS P50 Latency
**Median (P50) latency** representing typical user experience - 50% of operations complete faster than this value. Critical for understanding real-world performance expectations and user experience consistency.

![nonTLS P50 Latency](latency-nonTLS-p50-single.png)


#### nonTLS P99 Latency
**P99 latency** showing worst-case performance for 99% of operations. Higher P99 values indicate inconsistent performance or tail latency issues that can severely impact user experience during peak loads.

![nonTLS P99 Latency](latency-nonTLS-p99-single.png)


#### TLS AVG Latency
**Average latency** for Sets, Gets, and Totals operations across thread counts. Shows typical response time performance under different workloads. Lower values indicate better user experience and more responsive database operations.

![TLS AVG Latency](latency-TLS-avg-single.png)


#### TLS P50 Latency
**Median (P50) latency** representing typical user experience - 50% of operations complete faster than this value. Critical for understanding real-world performance expectations and user experience consistency.

![TLS P50 Latency](latency-TLS-p50-single.png)


#### TLS P99 Latency
**P99 latency** showing worst-case performance for 99% of operations. Higher P99 values indicate inconsistent performance or tail latency issues that can severely impact user experience during peak loads.

![TLS P99 Latency](latency-TLS-p99-single.png)


### Throughput Performance Charts


#### nonTLS Operations per Second
**Operations per second** for Sets, Gets, and Totals across thread configurations. Measures raw throughput capacity and scalability characteristics of each database. Higher values indicate better performance and ability to handle concurrent workloads.

![nonTLS Throughput](ops-nonTLS-single.png)


#### TLS Operations per Second
**Operations per second** for Sets, Gets, and Totals across thread configurations. Measures raw throughput capacity and scalability characteristics of each database. Higher values indicate better performance and ability to handle concurrent workloads.

![TLS Throughput](ops-TLS-single.png)


</details>

## Section B: Advanced Analysis Charts

<details>
<summary><strong>🔬 Advanced Performance Analysis</strong></summary>

### Database Comparison Charts


### Advanced Charts

*Advanced performance analysis charts are generated automatically.*
*The following charts may be available depending on test configuration:*

#### Non-TLS Performance Comparison
Side-by-side comparison of database performance

![Non-TLS Performance Comparison](advcharts-comparison.png)

#### TLS Performance Comparison
Side-by-side comparison with TLS encryption

![TLS Performance Comparison](advcharts-comparison-tls.png)

#### TLS vs Non-TLS Impact
Stacked view showing TLS overhead

![TLS vs Non-TLS Impact](advcharts-comparison-stack.png)

#### Non-TLS Scaling Analysis
Performance scaling across thread counts

![Non-TLS Scaling Analysis](advcharts-scaling.png)

#### TLS Scaling Analysis
TLS performance scaling patterns

![TLS Scaling Analysis](advcharts-scaling-tls.png)

#### Non-TLS Trade-off Analysis
Latency vs throughput relationships

![Non-TLS Trade-off Analysis](advcharts-tradeoff.png)

#### TLS Trade-off Analysis
TLS latency vs throughput trade-offs

![TLS Trade-off Analysis](advcharts-tradeoff-tls.png)

#### Non-TLS Cache Efficiency
Cache hit rates and performance

![Non-TLS Cache Efficiency](advcharts-cache.png)

#### TLS Cache Efficiency
TLS cache performance analysis

![TLS Cache Efficiency](advcharts-cache-tls.png)

#### Non-TLS Latency Distribution
Average vs P99 latency trends

![Non-TLS Latency Distribution](advcharts-latency-dist.png)

#### TLS Latency Distribution
TLS latency consistency analysis

![TLS Latency Distribution](advcharts-latency-dist-tls.png)

#### Non-TLS Performance Radar
Multi-dimensional performance profiles

![Non-TLS Performance Radar](advcharts-radar.png)

#### TLS Performance Radar
TLS performance across dimensions

![TLS Performance Radar](advcharts-radar-tls.png)

#### Non-TLS Performance Heatmap
Performance matrix visualization

![Non-TLS Performance Heatmap](advcharts-heatmap.png)

#### TLS Performance Heatmap
TLS performance patterns

![TLS Performance Heatmap](advcharts-heatmap-tls.png)


</details>

## Section C: PHP Redis Application Performance

<details>
<summary><strong>🐘 WordPress-Specific Performance Analysis</strong></summary>

#### Statistical Performance
WordPress-specific performance with quality indicators

![Statistical Performance](php_redis_statistical_performance.png)

#### Measurement Reliability
Coefficient of variation and quality analysis

![Measurement Reliability](php_redis_measurement_reliability.png)

#### Iteration Variance
Performance consistency across test runs

![Iteration Variance](php_redis_iteration_variance.png)

#### Confidence Intervals
Statistical significance analysis

![Confidence Intervals](php_redis_confidence_intervals.png)

#### Implementation Comparison
PHPRedis vs Predis comparison

![Implementation Comparison](php_redis_implementation_comparison.png)

#### Non-TLS Implementation Comparison
Pure performance comparison

![Non-TLS Implementation Comparison](php_redis_implementation_comparison_non_tls.png)

#### TLS Implementation Comparison
TLS reliability comparison

![TLS Implementation Comparison](php_redis_implementation_comparison_tls.png)

#### TLS Reliability Analysis
TLS success rates and stability

![TLS Reliability Analysis](php_redis_tls_reliability_analysis.png)

#### Statistical Comparison
Implementation reliability metrics

![Statistical Comparison](php_redis_statistical_comparison.png)


</details>

## Performance Interpretation Guide

### Key Metrics
- **Operations/Second**: Higher values indicate better throughput
- **Latency**: Lower values mean faster response times
- **P99 Latency**: 99th percentile - worst-case performance
- **CV**: Coefficient of Variation - consistency measure

### Chart Types
- **Bar Charts**: Direct performance comparisons
- **Line Charts**: Scaling trends and patterns
- **Scatter Plots**: Trade-off relationships
- **Radar Charts**: Multi-dimensional profiles
- **Heatmaps**: Performance pattern visualization

---
*Generated automatically by benchmarks-v6-host-phptests.yml workflow*
