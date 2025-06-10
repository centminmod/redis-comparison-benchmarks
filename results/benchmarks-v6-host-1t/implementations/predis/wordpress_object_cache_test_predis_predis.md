# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 04:49:59 UTC
**PHP Version:** 8.4.8
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
| Redis | Non-TLS | Predis | 14,908 | ±406 | 2.7% | 🟡 good | 0.067 | ±0.002 | 0.108 | 0.126 | 14,682-15,133 | 13 |
| Redis | TLS | Predis | 10,685 | ±299 | 2.8% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.169 | 10,519-10,851 | 13 |
| KeyDB | Non-TLS | Predis | 12,667 | ±363 | 2.9% | 🟡 good | 0.078 | ±0.002 | 0.123 | 0.144 | 12,465-12,868 | 13 |
| KeyDB | TLS | Predis | 9,575 | ±278 | 2.9% | 🟡 good | 0.104 | ±0.003 | 0.153 | 0.185 | 9,421-9,729 | 13 |
| Dragonfly | Non-TLS | Predis | 10,616 | ±308 | 2.9% | 🟡 good | 0.094 | ±0.003 | 0.143 | 0.172 | 10,445-10,786 | 13 |
| Dragonfly | TLS | Predis | 10,922 | ±289 | 2.6% | 🟡 good | 0.091 | ±0.003 | 0.136 | 0.162 | 10,761-11,082 | 13 |
| Valkey | Non-TLS | Predis | 14,925 | ±395 | 2.6% | 🟡 good | 0.067 | ±0.002 | 0.108 | 0.126 | 14,706-15,144 | 13 |
| Valkey | TLS | Predis | 10,645 | ±335 | 3.1% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.170 | 10,459-10,831 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,925 ops/sec
- **Average Performance:** 11,868 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
