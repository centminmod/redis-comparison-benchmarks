# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 00:09:38 UTC
**PHP Version:** 8.4.7
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
| Redis | Non-TLS | Predis | 10,470 | ±306 | 2.9% | 🟡 good | 0.095 | ±0.003 | 0.137 | 0.164 | 10,300-10,640 | 13 |
| Redis | TLS | Predis | 8,033 | ±227 | 2.8% | 🟡 good | 0.124 | ±0.004 | 0.174 | 0.212 | 7,907-8,158 | 13 |
| KeyDB | Non-TLS | Predis | 12,748 | ±338 | 2.7% | 🟡 good | 0.078 | ±0.002 | 0.121 | 0.142 | 12,561-12,935 | 13 |
| KeyDB | TLS | Predis | 9,645 | ±289 | 3.0% | 🟡 good | 0.103 | ±0.003 | 0.152 | 0.181 | 9,485-9,806 | 13 |
| Dragonfly | Non-TLS | Predis | 11,208 | ±344 | 3.1% | 🟡 good | 0.089 | ±0.003 | 0.137 | 0.165 | 11,017-11,398 | 13 |
| Dragonfly | TLS | Predis | 8,765 | ±227 | 2.6% | 🟡 good | 0.114 | ±0.003 | 0.165 | 0.203 | 8,639-8,891 | 13 |
| Valkey | Non-TLS | Predis | 15,057 | ±372 | 2.5% | 🟡 good | 0.066 | ±0.002 | 0.107 | 0.124 | 14,850-15,263 | 13 |
| Valkey | TLS | Predis | 10,777 | ±305 | 2.8% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.167 | 10,608-10,946 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,057 ops/sec
- **Average Performance:** 10,838 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
