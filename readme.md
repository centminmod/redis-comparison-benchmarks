# Redis vs KeyDB vs Dragonfly vs Valkey Performance Comparison

[![v1 Benchmark Redis vs KeyDB vs Dragonfly vs Valkey](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks.yml/badge.svg)](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks.yml) [![v4 Benchmark Redis vs KeyDB vs Dragonfly vs Valkey](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v4.yml/badge.svg)](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v4.yml) [![v5 Matrix Host Network Benchmark Redis vs KeyDB vs Dragonfly vs Valkey - Multi-Thread Tests](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v5-host.yml/badge.svg)](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v5-host.yml)

## Summary

This **v5 host-networked benchmark** compares four Redis-compatible engines - **Redis**, **KeyDB**, **Dragonfly**, and **Valkey** - on a 4 vCPU, 16 GB GitHub Actions Ubuntu runner. Each database runs in Docker **host** network mode (no NAT overhead), pinned to CPUs 0–3, and configured with 4 I/O threads (or proactors). Update: add [PHP Redis Benchmark Results](#8-addendum-php-redis-benchmark-results).

- [memtier_benchmark](https://github.com/RedisLabs/memtier_benchmark) (1:15 SET:GET, 512 B payload, Gaussian 3 M-key distribution)  
- Client threads = 1, 2, 4, 8  
- Clients/thread = 100, Requests/thread = 5 000, Pipeline = 1  

**Key points**  
- Prior Docker NAT-networked tests (see [readme-v2.md](readme-v2.md)) revealed a Valkey bug: `io-threads >1` regressed in performance.
- In this host-networked v5 test, that bug is resolved for Valkey which now scales properly with multiple I/O threads `io-threads >1`.  

Previous benchmarks:  
* v1 [Redis vs KeyDB vs Dragonfly](readme-v1.md)
* v2 [added Valkey, NAT-networked](readme-v2.md)

## Versions Tested

* Redis 8.0.2
* KeyDB 6.3.4
* Dragonfly 1.30.3
* Valkey 8.1.1

## Host-Networked 4-Thread Benchmarks (v5)

> **Environment:** GitHub Actions Azure Hosted runners with Ubuntu (4 vCPU, 16 GB RAM), Docker host network, CPU-pinning
> **Test tool:** `memtier_benchmark`  
> **Parameters:**  
> • Threads = 4  
> • Clients/thread = 100  
> • Requests/thread = 5 000  
> • Ratio = 1:15 SET:GET  
> • Data size = 512 Bytes  
> • Keyspace = 1…3 000 000 (Gaussian)  
> • IO-threads/Proactor = 4 
> • Full test results, charts are [here](/results/benchmarks-v5-host-4t-jun7-2025/)

---

## 1. Benchmark Commands

### 1.1 Non-TLS
```bash
memtier_benchmark \
  -s 127.0.0.1 --protocol=redis -p <port> \
  --ratio=1:15 --clients=100 --requests=5000 \
  --pipeline=1 --data-size=512 \
  --key-pattern=G:G --key-minimum=1 --key-maximum=3000000 \
  --key-median=1500000 --key-stddev=500000 \
  -t 4 --distinct-client-seed --hide-histogram
```

### 1.2 TLS
```bash
memtier_benchmark \
  -s 127.0.0.1 --protocol=redis -p <tls-port> --tls \
  --cert=test.crt --key=test.key --cacert=ca.crt --tls-skip-verify \
  --ratio=1:15 --clients=100 --requests=5000 \
  --pipeline=1 --data-size=512 \
  --key-pattern=G:G --key-minimum=1 --key-maximum=3000000 \
  --key-median=1500000 --key-stddev=500000 \
  -t 4 --distinct-client-seed --hide-histogram
```

---

## 2. Multi-Thread Summary

![Stacked non-TLS vs TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-comparison-stack.png)

### 2.1 Throughput & Avg Latency (Non-TLS)

![Stacked non-TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-comparison.png)

![Latency non-TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-latency-dist.png)

Github Hosted runners using Azure VM instances have 4 vCPU threads, so expected that 4 thread results were fastest. With 8 thread results showing the performance when there are not enough vCPU threads to service the load.

| Threads | Redis ops/s (avg lat) | KeyDB ops/s (avg lat) | Dragonfly ops/s (avg lat) | Valkey ops/s (avg lat) |
|-------:|----------------------:|----------------------:|--------------------------:|-----------------------:|
| **1**   | 61,112 (1.64 ms)     | 66,443 (1.50 ms)     | 53,113 (2.06 ms)         | 56,000 (1.79 ms)      |
| **2**   | 121,315 (1.65 ms)    | 102,536 (1.94 ms)    | 90,426 (2.70 ms)         | 68,335 (3.06 ms)      |
| **4**   | 125,524 (3.18 ms)    | 114,455 (3.51 ms)    | 119,615 (3.39 ms)        | 98,119 (4.15 ms)      |
| **8**   | 124,294 (6.52 ms)    | 111,217 (7.25 ms)    | 112,402 (7.30 ms)        | 104,091 (7.90 ms)     |

### 2.2 Throughput & Avg Latency (TLS)

![Stacked TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-comparison-tls.png)

![Latency TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-latency-dist-tls.png)

Github Hosted runners using Azure VM instances have 4 vCPU threads, so expected that 4 thread results were fastest. With 8 thread results showing the performance when there are not enough vCPU threads to service the load.

| Threads | Redis-TLS ops/s (avg lat) | KeyDB-TLS ops/s (avg lat) | Dragonfly-TLS ops/s (avg lat) | Valkey-TLS ops/s (avg lat) |
|-------:|--------------------------:|--------------------------:|------------------------------:|---------------------------:|
| **1**   | 45,867 (2.21 ms)         | 48,303 (2.07 ms)         | 34,756 (3.08 ms)             | 40,158 (2.55 ms)          |
| **2**   | 80,255 (2.50 ms)         | 75,470 (2.65 ms)         | 56,065 (4.02 ms)             | 47,790 (4.33 ms)          |
| **4**   | 83,563 (4.85 ms)         | 79,803 (4.92 ms)         | 79,232 (4.87 ms)             | 68,654 (6.17 ms)          |
| **8**   | 69,775 (11.75 ms)        | 68,785 (11.69 ms)        | 66,637 (11.98 ms)            | 69,007 (11.73 ms)         |

---

## 3. Cache Efficiency @ 4 Threads

![Cache Efficiency (Non-TLS)](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-cache-tls.png)  

*Non-TLS: all hit-rates ~5.15 %; absolute hits ∝ throughput*

![Cache Efficiency (TLS)](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-cache.png)  

*TLS: hit-rates unchanged, hits/s ↓ ~30 % across engines*

> **Insight:** Low hit-rate stems from large, random keyspace. Differences in hits/s map directly to raw throughput and TLS overhead.

---

## 4. Performance Heatmaps

For 4 threads:

| Metric           | Winner        | Comment                                             |
|:-----------------|:--------------|:----------------------------------------------------|
| **Throughput**   | Redis (125 524) & Dragonfly (119 615) | Redis edges out by ~5 %       |
| **Avg Latency**  | Redis (3.18 ms)                   | Dragonfly 3.39 ms; Valkey highest at 4.15 ms |
| **p99 Latency**  | Redis (7.65 ms) & Dragonfly (8.19 ms) | KeyDB/Valkey ~10 ms      |
| **p99.9 Latency**| Redis (16.19 ms)                  | Dragonfly/KeyDB ~17.9 ms; Valkey ~24.2 ms |

> **Note:** TLS multiplies latency ~1.5–2×, throughput ↓30 %, but relative ranking remains.

### 4.1 Non-TLS

![Heatmap Non-TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-heatmap.png)

### 4.2 TLS

![Heatmap TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-heatmap-tls.png)

---

## 5. Radar Profiles @ 4 Threads

**Axes (normalized):**  
- Throughput ↑  
- Low Latency (inverted ↑)  
- Cache Hit Rate ↑  
- Consistency (p99.9 inverted ↑)

| Engine      | Strengths                                    | Weaknesses                    |
|:------------|:---------------------------------------------|:-------------------------------|
| **Redis**      | Peak throughput & consistency, best latency   | Cache hit rate optimization    |
| **Dragonfly**  | Balanced performance, good scaling            | Moderate latency performance   |
| **KeyDB**      | Strong single-thread, good TLS resilience    | Higher tail latencies          |
| **Valkey**     | Improved multi-threading support             | Highest latencies overall      |

### 5.1 Non-TLS

![Radar Non-TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-radar.png)

### 5.2 TLS  

![Radar TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-radar-tls.png)

---

## 6. Performance Analysis Summary

### 6.1 Scalability (1→4 Threads Non-TLS)
| Engine      | 1T ops/s | 4T ops/s | Uplift |
|:------------|---------:|---------:|-------:|
| Redis       |   61,112 |  125,524 | +105%  |
| Dragonfly   |   53,113 |  119,615 | +125%  |
| KeyDB       |   66,443 |  114,455 | +72%   |
| Valkey      |   56,000 |   98,119 | +75%   |

**Key Insights:**
- **Dragonfly** shows the best scalability with +125% improvement from 1→4 threads
- **Redis** demonstrates strong scaling at +105% despite starting from a mid-range baseline
- **KeyDB** and **Valkey** show more modest scaling improvements around +72-75%
- All databases show diminishing returns beyond 4 threads due to 4-vCPU host limitations

### 6.2 Latency Breakdown (4-Thread Non-TLS)
| Engine      | Avg (ms) | p50 (ms) | p99 (ms) | p99.9 (ms) |
|:------------|---------:|---------:|---------:|-----------:|
| Redis       | 3.18     | 3.04     | 7.65     | 16.19      |
| Dragonfly   | 3.39     | 3.52     | 8.19     | 17.92      |
| KeyDB       | 3.51     | 3.23     | 10.37    | 17.92      |
| Valkey      | 4.15     | 3.99     | 10.05    | 24.19      |

**Key Insights:**
- **Redis** provides the most consistent low-latency performance across all percentiles
- **Dragonfly** offers competitive average latency with slightly higher tail latencies
- **Valkey** shows the highest latencies, particularly at p99.9 (+49% vs Redis)

### 6.3 TLS Performance Impact (4-Thread Comparison)
| Engine      | Non-TLS ops/s | TLS ops/s | Throughput Impact | Latency Impact |
|:------------|-------------:|-----------:|------------------:|---------------:|
| Redis       |      125,524 |     83,563 | -33.4%            | +52% (1.5×)    |
| KeyDB       |      114,455 |     79,803 | -30.3%            | +40% (1.4×)    |
| Dragonfly   |      119,615 |     79,232 | -33.8%            | +44% (1.4×)    |
| Valkey      |       98,119 |     68,654 | -30.0%            | +49% (1.5×)    |

**TLS Overhead Summary:**
- **Throughput** degradation: 30–34% across all engines
- **Average latency** increase: 1.4–1.5× (40-52% higher)
- **KeyDB** shows the most TLS-resilient performance with lowest throughput impact
- **Tail latencies** remain within acceptable ranges for typical caching workloads

### 6.4 Winner by Category
- **Peak Throughput (Non-TLS):** Redis (125,524 ops/s)
- **Peak Throughput (TLS):** Redis (83,563 ops/s)
- **Best Scalability:** Dragonfly (+125% improvement)
- **Lowest Latency:** Redis (3.18ms avg, 7.65ms p99)
- **TLS Resilience:** KeyDB (-30.3% throughput, +40% latency)
- **Single Thread Champion:** KeyDB (66,443 ops/s)

---

## 7. Recommendations

| Engine      | Best for                                        | Thread Sweet Spot |
|:------------|:-------------------------------------------------|:------------------|
| **Redis**      | Ultra-low latency, peak throughput, predictable SLA | 1–4 threads       |
| **Dragonfly**  | Maximum multi-core scalability, throughput growth   | 2–4 threads       |
| **KeyDB**      | Single-thread performance + Redis compatibility      | 1–4 threads       |
| **Valkey**     | Redis-fork projects with moderate scaling needs     | 2–4 threads       |

> For TLS workloads, budget ~30–35% more CPU and expect ~1.4–1.5× higher latencies.

---

## 8. Addendum: PHP Redis Benchmark Results

* **Supplemental WordPress Object Cache Test:** PHP-based benchmarks (PHP 8.4) using actual WordPress cache patterns  
* **Test Date:** June 8, 2025  
* **Environment:** GitHub Actions Azure Hosted runners with Ubuntu (4 vCPU, 16 GB RAM), Docker host network

![PHP Redis Test](/results/benchmarks-v6-host-1t-jun8-2025/php_redis_iteration_variance.png)

![PHP Redis Test](/results/benchmarks-v6-host-1t-jun8-2025/php_redis_statistical_performance.png)

### 8.1 PHP WordPress Object Cache Test Overview

In addition to the memtier_benchmark results above, conducted a specialized PHP-based test simulating real WordPress Redis object caching patterns. This test provides insights into how these databases perform with actual WordPress workloads.

**Test Configuration:**

**Tool:** Custom PHP WordPress Redis benchmark suite
- **Implementation:** Native PHP 8.4.7 with Redis extension 6.2.0
- **Architecture:** Single-threaded PHP application simulating WordPress object cache patterns
- **Framework:** Custom `RedisTestBase` class with WordPress-specific implementations

**Thread Configuration:** 1 thread per database
- `redis_io_threads=1` (Redis I/O thread configuration)
- `keydb_server_threads=1` (KeyDB server thread configuration) 
- `dragonfly_proactor_threads=1` (Dragonfly proactor thread configuration)
- `valkey_io_threads=1` (Valkey I/O thread configuration)

**Test Methodology:**
- **Operations:** 100,000 operations per iteration (configurable via `$operations` parameter)
- **Duration Control:** Both operation count and time-based limits (30 seconds max per iteration)
- **Read/Write Ratio:** 70% reads (GET), 30% writes (SETEX with TTL)
- **Cache Warmup:** 100 initial keys populated before each test iteration
- **Pause Strategy:** 0.1ms pause every 1,000 operations to simulate real-world usage patterns

**WordPress-Specific Key Patterns:**
- **Cache Groups:** `posts`, `terms`, `users`, `options`, `comments`, `themes`, `plugins`, `transients`, `site-options`
- **Key Formats:** 
  - `wp_cache_{group}_{id}` (standard WordPress cache keys)
  - `{group}_meta_{id}` (metadata cache keys)
  - `wp_option_{group}_{id}` (options cache keys)
  - `query_{group}_{hash}` (query result cache keys)
  - `transient_{group}_{id}` (transient cache keys)
  - `user_meta_{id}_{group}`, `post_meta_{id}_{group}`, `taxonomy_{group}_{id}`

**WordPress-Realistic Data Values:**
- **Simple values:** Strings, numbers, booleans (typical WordPress cache data)
- **Serialized PHP arrays:** Post objects, user metadata, complex WordPress data structures
- **JSON data:** API responses, structured data (100-1000 character payloads)
- **Large content:** Page cache content (simulated with 50-200 repeated content blocks)
- **Variable size:** Randomized content sizes reflecting real WordPress cache diversity

**TTL (Time-To-Live) Configuration:**
- **Range:** 5 minutes to 24 hours (300-86,400 seconds)
- **Distribution:** Random TTL assignment per operation
- **WordPress-typical:** Mirrors real WordPress cache expiration patterns
- **Cache Miss Simulation:** 20% chance to populate missing keys during read operations

**Statistical Methodology:**
- **Iterations:** 13 iterations per database (statistically significant sample size)
- **Inter-iteration Pause:** 500ms between iterations to ensure clean separation
- **Quality Measurement:** Coefficient of Variation (CV) analysis
  - Excellent: <2% CV
  - Good: <5% CV  
  - Fair: <10% CV
- **Confidence Intervals:** 95% confidence level with margin of error calculation
- **Latency Sampling:** Full latency measurement for all 100,000 operations per iteration

**Database State Management:**
- **Pre-test Cleanup:** `FLUSHALL` executed before each database test
- **Initial State:** Clean database with zero existing keys
- **Final State:** ~395,000 keys remaining after test completion
- **Connection Management:** Fresh Redis connections per test iteration

**Error Handling & Reliability:**
- **Exception Tracking:** Full error capture with detailed logging
- **Operation Counting:** Separate tracking of successful operations vs. errors
- **Timeout Protection:** Maximum duration limits prevent hung tests
- **Connection Recovery:** Automatic retry mechanisms for transient failures

**Performance Metrics Captured:**
- **Throughput:** Operations per second (primary performance indicator)
- **Latency Distribution:** Average, P95, P99 percentiles in milliseconds
- **Error Rates:** Failed operations as percentage of total attempts
- **Statistical Confidence:** CV, standard deviation, confidence intervals
- **WordPress-Specific:** Estimated page load capacity and concurrent user support

### 8.2 Single-Thread PHP Test Results

| Database | TLS | Avg Ops/sec | Avg Latency (ms) | P95 Latency (ms) | P99 Latency (ms) | Measurement Quality | CV |
|----------|-----|-------------|------------------|------------------|------------------|--------------------|----|
| Redis | Non-TLS | 16,605 | 0.0597 | 0.102 | 0.130 | Good | 2.14% |
| KeyDB | Non-TLS | 14,054 | 0.0705 | 0.127 | 0.146 | Good | 2.14% |
| Dragonfly | Non-TLS | 11,507 | 0.0861 | 0.160 | 0.186 | Good | 2.57% |
| Valkey | Non-TLS | 16,561 | 0.0598 | 0.103 | 0.131 | Good | 2.04% |

### 8.3 WordPress Performance Analysis

**Real-World WordPress Capacity Estimates:**

| Database | Light Pages/sec** | Heavy Pages/sec*** | Concurrent Users**** | Daily Page Views |
|----------|-------------------|--------------------|--------------------|------------------|
| Redis | 1,661 | 332 | 553 | 143,462,400 |
| KeyDB | 1,405 | 281 | 468 | 121,427,200 |
| Dragonfly | 1,151 | 230 | 384 | 99,420,800 |
| Valkey | 1,656 | 331 | 552 | 143,086,400 |

**Calculation Notes:**
- **Light Pages/sec: Assuming 10 cache operations per page load
- ***Heavy Pages/sec: Assuming 50 cache operations per page load  
- ****Concurrent Users: Assuming 30 cache operations per user per second
- Daily calculations: Light pages/sec × 86,400 seconds

### 8.4 PHP vs Memtier Performance Comparison

**Single Thread Comparison (1T Non-TLS):**

| Database | Memtier Ops/sec | PHP Ops/sec | Performance Ratio | Difference |
|----------|-----------------|-------------|-------------------|------------|
| Redis | 61,112 | 16,605 | 3.68× | Memtier +268% |
| KeyDB | 66,443 | 14,054 | 4.73× | Memtier +373% |
| Dragonfly | 53,113 | 11,507 | 4.61× | Memtier +361% |
| Valkey | 56,000 | 16,561 | 3.38× | Memtier +238% |

### 8.5 Key Insights from PHP Testing

**Performance Characteristics:**
1. **Redis leads in PHP-based tests** with highest ops/sec (16,605 ops/sec, 0.0597ms latency)
2. **Valkey just slightly behind (16,561) and lowest latency (0.0598ms)
3. **KeyDB performance gap is significant** in PHP tests, showing 15-18% lower throughput than Redis/Valkey
4. **Dragonfly shows consistent behavior** across both test methodologies with lowest throughput but stable performance

**Latency Analysis:**
- **Sub-millisecond latencies** achieved by Redis (0.0597ms) and Valkey (0.0598ms)
- **P99 latencies remain excellent** across all databases (<200ms, specifically 130-186ms range)

**Statistical Reliability:**
- All measurements achieved "Good" quality rating (CV < 5%)
- **Valkey most consistent** with lowest coefficient of variation (2.04%)
- **KeyDB and Redis tied** for second-best consistency (2.14% CV each)
- **13-iteration methodology** provides robust statistical confidence

### 8.6 WordPress Deployment Recommendations

**Database Selection for WordPress:**

| Use Case | Recommended Database | Rationale |
|----------|---------------------|-----------|
| **High-Traffic WordPress** | Valkey or Redis | Highest throughput, lowest latency, Redis-compatible |
| **WordPress Multisite** | Valkey | Best performance, Redis-compatible, active development |
| **Budget-Conscious WordPress** | KeyDB | Good performance, multi-threading benefits for mixed workloads |
| **Modern WordPress Stack** | Dragonfly | Excellent scaling characteristics, modern architecture |

**Capacity Planning:**
- **Redis:** Support ~1,661 light pages/sec or ~332 heavy pages/sec  
- **Valkey:** Support ~1,656 light pages/sec or ~331 heavy pages/sec
- **KeyDB:** Support ~1,405 light pages/sec or ~281 heavy pages/sec  
- **Dragonfly:** Support ~1,151 light pages/sec or ~230 heavy pages/sec

