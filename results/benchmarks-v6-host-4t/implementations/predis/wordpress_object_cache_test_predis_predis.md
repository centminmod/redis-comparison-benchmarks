# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 04:52:17 UTC
**PHP Version:** 8.4.8
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
| Redis | Non-TLS | Predis | 10,271 | ±271 | 2.6% | 🟡 good | 0.097 | ±0.003 | 0.140 | 0.169 | 10,121-10,421 | 13 |
| Redis | TLS | Predis | 7,820 | ±244 | 3.1% | 🟡 good | 0.127 | ±0.004 | 0.179 | 0.223 | 7,685-7,956 | 13 |
| KeyDB | Non-TLS | Predis | 12,343 | ±354 | 2.9% | 🟡 good | 0.081 | ±0.003 | 0.125 | 0.149 | 12,146-12,540 | 13 |
| KeyDB | TLS | Predis | 9,457 | ±301 | 3.2% | 🟡 good | 0.105 | ±0.004 | 0.155 | 0.186 | 9,290-9,624 | 13 |
| Dragonfly | Non-TLS | Predis | 10,600 | ±277 | 2.6% | 🟡 good | 0.094 | ±0.003 | 0.140 | 0.167 | 10,446-10,753 | 13 |
| Dragonfly | TLS | Predis | 7,533 | ±192 | 2.6% | 🟡 good | 0.132 | ±0.004 | 0.182 | 0.224 | 7,426-7,639 | 13 |
| Valkey | Non-TLS | Predis | 14,724 | ±367 | 2.5% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.128 | 14,521-14,927 | 13 |
| Valkey | TLS | Predis | 10,463 | ±307 | 2.9% | 🟡 good | 0.095 | ±0.003 | 0.145 | 0.173 | 10,293-10,634 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,724 ops/sec
- **Average Performance:** 10,401 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
