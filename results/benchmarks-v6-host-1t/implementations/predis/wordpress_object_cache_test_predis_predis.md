# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 18:55:05 UTC
**PHP Version:** 8.4.8
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 7
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
| Redis | Non-TLS | Predis | 14,774 | ±368 | 2.5% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.125 | 14,570-14,978 | 13 |
| Redis | TLS | Predis | 10,703 | ±319 | 3.0% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.168 | 10,526-10,880 | 13 |
| KeyDB | Non-TLS | Predis | 12,703 | ±356 | 2.8% | 🟡 good | 0.078 | ±0.002 | 0.122 | 0.142 | 12,505-12,900 | 13 |
| KeyDB | TLS | Predis | 9,659 | ±271 | 2.8% | 🟡 good | 0.103 | ±0.003 | 0.151 | 0.179 | 9,509-9,809 | 13 |
| Dragonfly | Non-TLS | Predis | 10,690 | ±247 | 2.3% | 🟡 good | 0.093 | ±0.002 | 0.138 | 0.162 | 10,553-10,827 | 13 |
| Valkey | Non-TLS | Predis | 14,770 | ±474 | 3.2% | 🟡 good | 0.067 | ±0.002 | 0.108 | 0.125 | 14,507-15,033 | 13 |
| Valkey | TLS | Predis | 10,692 | ±288 | 2.7% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.167 | 10,532-10,851 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,774 ops/sec
- **Average Performance:** 11,999 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
