# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 10:20:03 UTC
**PHP Version:** 8.4.8
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
**Thread Variant:** 1

## Predis Configuration

- **Connection Timeout:** 5s
- **Read/Write Timeout:** 5s
- **TCP Keepalive:** Enabled
- **Persistent Connections:** Disabled
- **Connection Retry Attempts:** 3

## Statistical Methodology

- **Iterations per Test:** 13
- **Iteration Pause:** 500ms
- **Statistical Measures:** Standard deviation, coefficient of variation, 95% confidence intervals
- **Quality Thresholds:** Excellent (<2% CV), Good (<5% CV), Fair (<10% CV), Poor (≥10% CV)

## Thread Configuration

- **redis_io_threads:** 1
- **keydb_server_threads:** 1
- **dragonfly_proactor_threads:** 1
- **valkey_io_threads:** 1

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 14,815 | ±409 | 2.8% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.126 | 14,589-15,042 | 13 |
| Redis | TLS | Predis | 10,694 | ±315 | 2.9% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.167 | 10,519-10,869 | 13 |
| KeyDB | Non-TLS | Predis | 12,744 | ±333 | 2.6% | 🟡 good | 0.078 | ±0.002 | 0.122 | 0.142 | 12,559-12,929 | 13 |
| KeyDB | TLS | Predis | 9,737 | ±294 | 3.0% | 🟡 good | 0.102 | ±0.003 | 0.150 | 0.178 | 9,574-9,901 | 13 |
| Dragonfly | Non-TLS | Predis | 10,735 | ±296 | 2.8% | 🟡 good | 0.093 | ±0.003 | 0.137 | 0.162 | 10,571-10,899 | 13 |
| Dragonfly | TLS | Predis | 11,191 | ±330 | 3.0% | 🟡 good | 0.089 | ±0.003 | 0.131 | 0.156 | 11,007-11,374 | 13 |
| Valkey | Non-TLS | Predis | 14,807 | ±386 | 2.6% | 🟡 good | 0.067 | ±0.002 | 0.108 | 0.125 | 14,593-15,021 | 13 |
| Valkey | TLS | Predis | 10,682 | ±274 | 2.6% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.167 | 10,530-10,834 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,815 ops/sec
- **Average Performance:** 11,926 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
