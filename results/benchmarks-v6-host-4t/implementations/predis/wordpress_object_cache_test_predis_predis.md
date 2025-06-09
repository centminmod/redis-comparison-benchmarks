# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 04:14:50 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
**Thread Variant:** 4

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

- **redis_io_threads:** 4
- **keydb_server_threads:** 4
- **dragonfly_proactor_threads:** 4
- **valkey_io_threads:** 4

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 10,331 | ±310 | 3.0% | 🟡 good | 0.096 | ±0.003 | 0.138 | 0.166 | 10,159-10,503 | 13 |
| Redis | TLS | Predis | 7,925 | ±201 | 2.5% | 🟡 good | 0.126 | ±0.003 | 0.176 | 0.217 | 7,814-8,037 | 13 |
| KeyDB | Non-TLS | Predis | 12,705 | ±346 | 2.7% | 🟡 good | 0.078 | ±0.002 | 0.122 | 0.143 | 12,513-12,897 | 13 |
| KeyDB | TLS | Predis | 9,718 | ±266 | 2.7% | 🟡 good | 0.102 | ±0.003 | 0.151 | 0.179 | 9,570-9,866 | 13 |
| Dragonfly | Non-TLS | Predis | 10,610 | ±324 | 3.1% | 🟡 good | 0.094 | ±0.003 | 0.139 | 0.165 | 10,430-10,790 | 13 |
| Dragonfly | TLS | Predis | 8,281 | ±224 | 2.7% | 🟡 good | 0.120 | ±0.003 | 0.174 | 0.211 | 8,157-8,405 | 13 |
| Valkey | Non-TLS | Predis | 14,878 | ±395 | 2.7% | 🟡 good | 0.067 | ±0.002 | 0.107 | 0.125 | 14,660-15,097 | 13 |
| Valkey | TLS | Predis | 10,801 | ±304 | 2.8% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.167 | 10,633-10,970 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,878 ops/sec
- **Average Performance:** 10,656 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
