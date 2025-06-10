# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 07:41:14 UTC
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
| Redis | Non-TLS | Predis | 10,245 | ±316 | 3.1% | 🟡 good | 0.097 | ±0.003 | 0.140 | 0.168 | 10,070-10,420 | 13 |
| Redis | TLS | Predis | 7,916 | ±250 | 3.2% | 🟡 good | 0.126 | ±0.004 | 0.178 | 0.216 | 7,778-8,055 | 13 |
| KeyDB | Non-TLS | Predis | 12,572 | ±301 | 2.4% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.143 | 12,405-12,739 | 13 |
| KeyDB | TLS | Predis | 9,505 | ±266 | 2.8% | 🟡 good | 0.105 | ±0.003 | 0.154 | 0.184 | 9,357-9,652 | 13 |
| Dragonfly | Non-TLS | Predis | 10,487 | ±286 | 2.7% | 🟡 good | 0.095 | ±0.003 | 0.140 | 0.166 | 10,328-10,645 | 13 |
| Dragonfly | TLS | Predis | 8,465 | ±196 | 2.3% | 🟡 good | 0.118 | ±0.003 | 0.174 | 0.208 | 8,356-8,574 | 13 |
| Valkey | Non-TLS | Predis | 14,427 | ±363 | 2.5% | 🟡 good | 0.069 | ±0.002 | 0.111 | 0.128 | 14,226-14,628 | 13 |
| Valkey | TLS | Predis | 10,325 | ±310 | 3.0% | 🟡 good | 0.096 | ±0.003 | 0.146 | 0.173 | 10,153-10,497 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,427 ops/sec
- **Average Performance:** 10,493 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
