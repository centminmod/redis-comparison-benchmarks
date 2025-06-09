# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 04:15:38 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
**Thread Variant:** 2

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

- **redis_io_threads:** 2
- **keydb_server_threads:** 2
- **dragonfly_proactor_threads:** 2
- **valkey_io_threads:** 2

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 10,470 | ±295 | 2.8% | 🟡 good | 0.095 | ±0.003 | 0.137 | 0.162 | 10,306-10,634 | 13 |
| Redis | TLS | Predis | 8,038 | ±217 | 2.7% | 🟡 good | 0.124 | ±0.004 | 0.173 | 0.210 | 7,918-8,159 | 13 |
| KeyDB | Non-TLS | Predis | 12,758 | ±355 | 2.8% | 🟡 good | 0.078 | ±0.002 | 0.121 | 0.142 | 12,561-12,955 | 13 |
| KeyDB | TLS | Predis | 9,693 | ±268 | 2.8% | 🟡 good | 0.103 | ±0.003 | 0.151 | 0.180 | 9,545-9,841 | 13 |
| Dragonfly | Non-TLS | Predis | 11,169 | ±335 | 3.0% | 🟡 good | 0.089 | ±0.003 | 0.137 | 0.165 | 10,983-11,354 | 13 |
| Dragonfly | TLS | Predis | 8,328 | ±251 | 3.0% | 🟡 good | 0.120 | ±0.004 | 0.172 | 0.207 | 8,189-8,467 | 13 |
| Valkey | Non-TLS | Predis | 15,029 | ±386 | 2.6% | 🟡 good | 0.066 | ±0.002 | 0.106 | 0.123 | 14,815-15,243 | 13 |
| Valkey | TLS | Predis | 10,853 | ±323 | 3.0% | 🟡 good | 0.092 | ±0.003 | 0.140 | 0.165 | 10,674-11,032 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,029 ops/sec
- **Average Performance:** 10,792 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
