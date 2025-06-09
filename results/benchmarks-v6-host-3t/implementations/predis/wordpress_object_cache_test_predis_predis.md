# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 07:50:34 UTC
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
| Redis | Non-TLS | Predis | 10,463 | ±307 | 2.9% | 🟡 good | 0.095 | ±0.003 | 0.137 | 0.164 | 10,293-10,634 | 13 |
| Redis | TLS | Predis | 8,056 | ±234 | 2.9% | 🟡 good | 0.124 | ±0.004 | 0.173 | 0.212 | 7,927-8,186 | 13 |
| KeyDB | Non-TLS | Predis | 12,687 | ±340 | 2.7% | 🟡 good | 0.078 | ±0.002 | 0.122 | 0.142 | 12,499-12,876 | 13 |
| KeyDB | TLS | Predis | 9,701 | ±271 | 2.8% | 🟡 good | 0.103 | ±0.003 | 0.151 | 0.179 | 9,551-9,851 | 13 |
| Dragonfly | Non-TLS | Predis | 10,597 | ±249 | 2.3% | 🟡 good | 0.094 | ±0.002 | 0.139 | 0.164 | 10,459-10,735 | 13 |
| Dragonfly | TLS | Predis | 8,750 | ±201 | 2.3% | 🟡 good | 0.114 | ±0.003 | 0.165 | 0.203 | 8,639-8,862 | 13 |
| Valkey | Non-TLS | Predis | 14,989 | ±373 | 2.5% | 🟡 good | 0.066 | ±0.002 | 0.107 | 0.125 | 14,782-15,196 | 13 |
| Valkey | TLS | Predis | 10,660 | ±325 | 3.1% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.168 | 10,479-10,840 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,989 ops/sec
- **Average Performance:** 10,738 ops/sec
- **Average Measurement Precision:** 2.7% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
