# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 15:31:50 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 7
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
| Redis | Non-TLS | Predis | 10,408 | ±309 | 3.0% | 🟡 good | 0.096 | ±0.003 | 0.138 | 0.164 | 10,236-10,579 | 13 |
| Redis | TLS | Predis | 8,080 | ±253 | 3.1% | 🟡 good | 0.123 | ±0.004 | 0.173 | 0.212 | 7,940-8,221 | 13 |
| KeyDB | Non-TLS | Predis | 12,725 | ±343 | 2.7% | 🟡 good | 0.078 | ±0.002 | 0.121 | 0.141 | 12,535-12,916 | 13 |
| KeyDB | TLS | Predis | 9,772 | ±284 | 2.9% | 🟡 good | 0.102 | ±0.003 | 0.151 | 0.179 | 9,615-9,929 | 13 |
| Dragonfly | Non-TLS | Predis | 10,936 | ±312 | 2.9% | 🟡 good | 0.091 | ±0.003 | 0.140 | 0.167 | 10,763-11,110 | 13 |
| Valkey | Non-TLS | Predis | 14,962 | ±395 | 2.6% | 🟡 good | 0.066 | ±0.002 | 0.107 | 0.125 | 14,743-15,181 | 13 |
| Valkey | TLS | Predis | 10,783 | ±283 | 2.6% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.167 | 10,626-10,940 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,962 ops/sec
- **Average Performance:** 11,095 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
