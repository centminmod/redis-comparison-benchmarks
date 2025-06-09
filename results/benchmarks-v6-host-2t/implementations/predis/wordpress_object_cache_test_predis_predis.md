# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 11:44:08 UTC
**PHP Version:** 8.4.7
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
| Redis | Non-TLS | Predis | 10,422 | ±277 | 2.7% | 🟡 good | 0.095 | ±0.003 | 0.137 | 0.164 | 10,268-10,575 | 13 |
| Redis | TLS | Predis | 7,968 | ±253 | 3.2% | 🟡 good | 0.125 | ±0.004 | 0.176 | 0.215 | 7,828-8,109 | 13 |
| KeyDB | Non-TLS | Predis | 12,730 | ±382 | 3.0% | 🟡 good | 0.078 | ±0.003 | 0.122 | 0.142 | 12,519-12,942 | 13 |
| KeyDB | TLS | Predis | 9,629 | ±266 | 2.8% | 🟡 good | 0.103 | ±0.003 | 0.152 | 0.181 | 9,481-9,776 | 13 |
| Dragonfly | Non-TLS | Predis | 10,736 | ±284 | 2.6% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.170 | 10,578-10,893 | 13 |
| Valkey | Non-TLS | Predis | 15,021 | ±390 | 2.6% | 🟡 good | 0.066 | ±0.002 | 0.107 | 0.125 | 14,805-15,238 | 13 |
| Valkey | TLS | Predis | 10,700 | ±328 | 3.1% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.168 | 10,518-10,882 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,021 ops/sec
- **Average Performance:** 11,029 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
