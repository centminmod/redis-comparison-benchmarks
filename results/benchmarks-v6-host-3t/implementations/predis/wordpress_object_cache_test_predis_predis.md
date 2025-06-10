# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 11:00:48 UTC
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

- **Iterations per Test:** 5
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
| Redis | Non-TLS | Predis | 9,643 | ±436 | 4.5% | 🟡 good | 0.103 | ±0.005 | 0.175 | 0.221 | 9,103-10,184 | 5 |
| Redis | TLS | Predis | 7,378 | ±308 | 4.2% | 🟡 good | 0.135 | ±0.006 | 0.231 | 0.288 | 6,996-7,760 | 5 |
| KeyDB | Non-TLS | Predis | 11,850 | ±549 | 4.6% | 🟡 good | 0.084 | ±0.004 | 0.144 | 0.184 | 11,168-12,531 | 5 |
| KeyDB | TLS | Predis | 8,919 | ±381 | 4.3% | 🟡 good | 0.112 | ±0.005 | 0.190 | 0.244 | 8,446-9,392 | 5 |
| Dragonfly | Non-TLS | Predis | 10,048 | ±403 | 4.0% | 🟡 good | 0.099 | ±0.004 | 0.169 | 0.229 | 9,548-10,549 | 5 |
| Dragonfly | TLS | Predis | 7,777 | ±245 | 3.1% | 🟡 good | 0.128 | ±0.004 | 0.213 | 0.287 | 7,473-8,081 | 5 |
| Valkey | Non-TLS | Predis | 13,986 | ±619 | 4.4% | 🟡 good | 0.071 | ±0.003 | 0.124 | 0.161 | 13,217-14,754 | 5 |
| Valkey | TLS | Predis | 10,014 | ±531 | 5.3% | 🟠 fair | 0.100 | ±0.006 | 0.170 | 0.226 | 9,355-10,673 | 5 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 13,986 ops/sec
- **Average Performance:** 9,952 ops/sec
- **Average Measurement Precision:** 4.3% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
