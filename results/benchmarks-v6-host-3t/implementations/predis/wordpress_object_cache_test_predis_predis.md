# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 10:11:47 UTC
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
| Redis | Non-TLS | Predis | 10,312 | ±292 | 2.8% | 🟡 good | 0.097 | ±0.003 | 0.139 | 0.167 | 10,150-10,474 | 13 |
| Redis | TLS | Predis | 7,923 | ±227 | 2.9% | 🟡 good | 0.126 | ±0.004 | 0.176 | 0.216 | 7,797-8,049 | 13 |
| KeyDB | Non-TLS | Predis | 12,556 | ±316 | 2.5% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.144 | 12,381-12,732 | 13 |
| KeyDB | TLS | Predis | 9,537 | ±281 | 2.9% | 🟡 good | 0.104 | ±0.003 | 0.153 | 0.182 | 9,382-9,693 | 13 |
| Dragonfly | Non-TLS | Predis | 10,630 | ±267 | 2.5% | 🟡 good | 0.094 | ±0.003 | 0.144 | 0.171 | 10,482-10,779 | 13 |
| Dragonfly | TLS | Predis | 8,182 | ±239 | 2.9% | 🟡 good | 0.122 | ±0.004 | 0.175 | 0.214 | 8,049-8,314 | 13 |
| Valkey | Non-TLS | Predis | 14,745 | ±392 | 2.7% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.127 | 14,527-14,962 | 13 |
| Valkey | TLS | Predis | 10,630 | ±304 | 2.9% | 🟡 good | 0.094 | ±0.003 | 0.143 | 0.170 | 10,461-10,798 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,745 ops/sec
- **Average Performance:** 10,564 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
