# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 11:02:13 UTC
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

- **Iterations per Test:** 5
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
| Redis | Non-TLS | Predis | 13,812 | ±642 | 4.6% | 🟡 good | 0.072 | ±0.003 | 0.123 | 0.163 | 13,016-14,609 | 5 |
| Redis | TLS | Predis | 9,961 | ±476 | 4.8% | 🟡 good | 0.100 | ±0.005 | 0.171 | 0.230 | 9,370-10,552 | 5 |
| KeyDB | Non-TLS | Predis | 12,049 | ±577 | 4.8% | 🟡 good | 0.083 | ±0.004 | 0.141 | 0.180 | 11,332-12,765 | 5 |
| KeyDB | TLS | Predis | 9,060 | ±392 | 4.3% | 🟡 good | 0.110 | ±0.005 | 0.186 | 0.239 | 8,573-9,547 | 5 |
| Dragonfly | Non-TLS | Predis | 9,997 | ±471 | 4.7% | 🟡 good | 0.100 | ±0.005 | 0.168 | 0.228 | 9,412-10,581 | 5 |
| Dragonfly | TLS | Predis | 10,728 | ±680 | 6.3% | 🟠 fair | 0.093 | ±0.006 | 0.153 | 0.196 | 9,884-11,572 | 5 |
| Valkey | Non-TLS | Predis | 14,089 | ±540 | 3.8% | 🟡 good | 0.071 | ±0.003 | 0.120 | 0.161 | 13,418-14,759 | 5 |
| Valkey | TLS | Predis | 10,057 | ±452 | 4.5% | 🟡 good | 0.099 | ±0.005 | 0.165 | 0.226 | 9,496-10,618 | 5 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,089 ops/sec
- **Average Performance:** 11,219 ops/sec
- **Average Measurement Precision:** 4.7% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
