# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 18:57:09 UTC
**PHP Version:** 8.4.8
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 7
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
| Redis | Non-TLS | Predis | 10,296 | ±279 | 2.7% | 🟡 good | 0.097 | ±0.003 | 0.139 | 0.166 | 10,141-10,450 | 13 |
| Redis | TLS | Predis | 7,819 | ±235 | 3.0% | 🟡 good | 0.127 | ±0.004 | 0.179 | 0.217 | 7,688-7,949 | 13 |
| KeyDB | Non-TLS | Predis | 12,516 | ±348 | 2.8% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.144 | 12,323-12,709 | 13 |
| KeyDB | TLS | Predis | 9,483 | ±285 | 3.0% | 🟡 good | 0.105 | ±0.003 | 0.154 | 0.183 | 9,325-9,641 | 13 |
| Dragonfly | Non-TLS | Predis | 10,446 | ±274 | 2.6% | 🟡 good | 0.095 | ±0.003 | 0.141 | 0.167 | 10,294-10,598 | 13 |
| Valkey | Non-TLS | Predis | 14,382 | ±393 | 2.7% | 🟡 good | 0.069 | ±0.002 | 0.111 | 0.128 | 14,164-14,600 | 13 |
| Valkey | TLS | Predis | 10,387 | ±298 | 2.9% | 🟡 good | 0.096 | ±0.003 | 0.145 | 0.171 | 10,222-10,553 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,382 ops/sec
- **Average Performance:** 10,761 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
