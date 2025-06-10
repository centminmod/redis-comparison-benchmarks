# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 07:38:58 UTC
**PHP Version:** 8.4.8
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
**Thread Variant:** 3

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

- **redis_io_threads:** 3
- **keydb_server_threads:** 3
- **dragonfly_proactor_threads:** 3
- **valkey_io_threads:** 3

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 10,276 | ±278 | 2.7% | 🟡 good | 0.097 | ±0.003 | 0.140 | 0.169 | 10,122-10,430 | 13 |
| Redis | TLS | Predis | 7,891 | ±226 | 2.9% | 🟡 good | 0.126 | ±0.004 | 0.177 | 0.217 | 7,765-8,016 | 13 |
| KeyDB | Non-TLS | Predis | 12,548 | ±344 | 2.7% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.145 | 12,357-12,739 | 13 |
| KeyDB | TLS | Predis | 9,589 | ±315 | 3.3% | 🟡 good | 0.104 | ±0.004 | 0.153 | 0.182 | 9,414-9,764 | 13 |
| Dragonfly | Non-TLS | Predis | 11,065 | ±346 | 3.1% | 🟡 good | 0.090 | ±0.003 | 0.139 | 0.169 | 10,873-11,257 | 13 |
| Dragonfly | TLS | Predis | 8,112 | ±245 | 3.0% | 🟡 good | 0.123 | ±0.004 | 0.177 | 0.216 | 7,976-8,248 | 13 |
| Valkey | Non-TLS | Predis | 14,750 | ±422 | 2.9% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.128 | 14,516-14,984 | 13 |
| Valkey | TLS | Predis | 10,621 | ±307 | 2.9% | 🟡 good | 0.094 | ±0.003 | 0.143 | 0.169 | 10,450-10,791 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,750 ops/sec
- **Average Performance:** 10,606 ops/sec
- **Average Measurement Precision:** 2.9% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
