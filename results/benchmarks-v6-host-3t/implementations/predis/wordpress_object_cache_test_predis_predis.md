# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 04:51:24 UTC
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
| Redis | Non-TLS | Predis | 10,361 | ±292 | 2.8% | 🟡 good | 0.096 | ±0.003 | 0.139 | 0.165 | 10,199-10,523 | 13 |
| Redis | TLS | Predis | 8,043 | ±240 | 3.0% | 🟡 good | 0.124 | ±0.004 | 0.173 | 0.210 | 7,910-8,176 | 13 |
| KeyDB | Non-TLS | Predis | 12,793 | ±341 | 2.7% | 🟡 good | 0.078 | ±0.002 | 0.121 | 0.141 | 12,604-12,982 | 13 |
| KeyDB | TLS | Predis | 9,678 | ±271 | 2.8% | 🟡 good | 0.103 | ±0.003 | 0.151 | 0.180 | 9,528-9,828 | 13 |
| Dragonfly | Non-TLS | Predis | 10,806 | ±298 | 2.8% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.167 | 10,641-10,972 | 13 |
| Dragonfly | TLS | Predis | 8,370 | ±240 | 2.9% | 🟡 good | 0.119 | ±0.004 | 0.172 | 0.207 | 8,237-8,504 | 13 |
| Valkey | Non-TLS | Predis | 14,940 | ±341 | 2.3% | 🟡 good | 0.066 | ±0.002 | 0.107 | 0.124 | 14,751-15,129 | 13 |
| Valkey | TLS | Predis | 10,777 | ±305 | 2.8% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.166 | 10,608-10,946 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,940 ops/sec
- **Average Performance:** 10,721 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
