# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 04:57:03 UTC
**PHP Version:** 8.4.8
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
| Redis | Non-TLS | Predis | 10,343 | ±304 | 2.9% | 🟡 good | 0.096 | ±0.003 | 0.139 | 0.165 | 10,174-10,511 | 13 |
| Redis | TLS | Predis | 7,969 | ±241 | 3.0% | 🟡 good | 0.125 | ±0.004 | 0.176 | 0.213 | 7,835-8,102 | 13 |
| KeyDB | Non-TLS | Predis | 12,698 | ±376 | 3.0% | 🟡 good | 0.078 | ±0.003 | 0.122 | 0.142 | 12,490-12,907 | 13 |
| KeyDB | TLS | Predis | 9,656 | ±272 | 2.8% | 🟡 good | 0.103 | ±0.003 | 0.152 | 0.179 | 9,506-9,807 | 13 |
| Dragonfly | Non-TLS | Predis | 11,066 | ±313 | 2.8% | 🟡 good | 0.090 | ±0.003 | 0.138 | 0.165 | 10,893-11,240 | 13 |
| Dragonfly | TLS | Predis | 8,541 | ±266 | 3.1% | 🟡 good | 0.117 | ±0.004 | 0.173 | 0.206 | 8,393-8,688 | 13 |
| Valkey | Non-TLS | Predis | 14,636 | ±317 | 2.2% | 🟡 good | 0.068 | ±0.002 | 0.109 | 0.126 | 14,460-14,812 | 13 |
| Valkey | TLS | Predis | 10,425 | ±270 | 2.6% | 🟡 good | 0.095 | ±0.003 | 0.145 | 0.170 | 10,275-10,574 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,636 ops/sec
- **Average Performance:** 10,667 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
