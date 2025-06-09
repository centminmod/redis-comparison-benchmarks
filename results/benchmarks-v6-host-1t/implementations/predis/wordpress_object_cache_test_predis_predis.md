# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 07:46:33 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
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
| Redis | Non-TLS | Predis | 14,977 | ±414 | 2.8% | 🟡 good | 0.066 | ±0.002 | 0.107 | 0.125 | 14,747-15,206 | 13 |
| Redis | TLS | Predis | 10,805 | ±288 | 2.7% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.168 | 10,645-10,965 | 13 |
| KeyDB | Non-TLS | Predis | 12,581 | ±343 | 2.7% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.144 | 12,391-12,771 | 13 |
| KeyDB | TLS | Predis | 9,603 | ±270 | 2.8% | 🟡 good | 0.104 | ±0.003 | 0.152 | 0.182 | 9,453-9,753 | 13 |
| Dragonfly | Non-TLS | Predis | 10,502 | ±238 | 2.3% | 🟡 good | 0.095 | ±0.002 | 0.140 | 0.166 | 10,370-10,634 | 13 |
| Dragonfly | TLS | Predis | 7,887 | ±201 | 2.6% | 🟡 good | 0.126 | ±0.003 | 0.174 | 0.214 | 7,776-7,999 | 13 |
| Valkey | Non-TLS | Predis | 14,845 | ±390 | 2.6% | 🟡 good | 0.067 | ±0.002 | 0.107 | 0.125 | 14,628-15,061 | 13 |
| Valkey | TLS | Predis | 10,742 | ±327 | 3.0% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.168 | 10,561-10,924 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,977 ops/sec
- **Average Performance:** 11,493 ops/sec
- **Average Measurement Precision:** 2.7% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
