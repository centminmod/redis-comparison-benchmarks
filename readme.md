# Redis vs KeyDB vs Dragonfly vs Valkey Performance Comparison

[![v1 Benchmark Redis vs KeyDB vs Dragonfly vs Valkey](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks.yml/badge.svg)](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks.yml) [![v4 Benchmark Redis vs KeyDB vs Dragonfly vs Valkey](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v4.yml/badge.svg)](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v4.yml) [![v5 Matrix Host Network Benchmark Redis vs KeyDB vs Dragonfly vs Valkey - Multi-Thread Tests](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v5-host.yml/badge.svg)](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks-v5-host.yml)

## Summary

This **v5 host-networked benchmark** compares four Redis-compatible engines - **Redis**, **KeyDB**, **Dragonfly**, and **Valkey** - on a 4 vCPU, 16 GB GitHub Actions Ubuntu runner. Each database runs in Docker **host** network mode (no NAT overhead), pinned to CPUs 0–3, and configured with 4 I/O threads (or proactors).

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

Github Hosted runners using Azure VM instances have 4 vCPU threads, so expected that 4 thread results were fastest. With 8 thread results showing the performance when there are no enough vCPU threads to service the load.

| Threads | Redis ops/s (avg lat) | KeyDB ops/s (avg lat) | Dragonfly ops/s (avg lat) | Valkey ops/s (avg lat) |
|-------:|----------------------:|----------------------:|--------------------------:|-----------------------:|
| **1**   | 61,112 (1.64 ms)     | 66,443 (1.50 ms)     | 53,113 (2.06 ms)         | 56,000 (1.79 ms)      |
| **2**   | 121,315 (1.65 ms)    | 102,536 (1.94 ms)    | 90,426 (2.70 ms)         | 68,335 (3.06 ms)      |
| **4**   | 125,524 (3.18 ms)    | 114,455 (3.51 ms)    | 119,615 (3.39 ms)        | 98,119 (4.15 ms)      |
| **8**   | 124,294 (6.52 ms)    | 111,217 (7.25 ms)    | 112,402 (7.30 ms)        | 104,091 (7.90 ms)     |

### 2.2 Throughput & Avg Latency (TLS)

![Stacked TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-comparison-tls.png)

![Latency TLS](/results/benchmarks-v5-host-4t-jun7-2025/advcharts-latency-dist-tls.png)

Github Hosted runners using Azure VM instances have 4 vCPU threads, so expected that 4 thread results were fastest. With 8 thread results showing the performance when there are no enough vCPU threads to service the load.

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