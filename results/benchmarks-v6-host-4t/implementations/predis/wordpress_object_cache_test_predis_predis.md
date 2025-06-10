# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 10:12:55 UTC
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
| Redis | Non-TLS | Predis | 10,351 | ±299 | 2.9% | 🟡 good | 0.096 | ±0.003 | 0.139 | 0.166 | 10,185-10,517 | 13 |
| Redis | TLS | Predis | 7,903 | ±243 | 3.1% | 🟡 good | 0.126 | ±0.004 | 0.176 | 0.217 | 7,768-8,038 | 13 |
| KeyDB | Non-TLS | Predis | 12,694 | ±371 | 2.9% | 🟡 good | 0.078 | ±0.002 | 0.122 | 0.144 | 12,488-12,900 | 13 |
| KeyDB | TLS | Predis | 9,546 | ±266 | 2.8% | 🟡 good | 0.104 | ±0.003 | 0.154 | 0.184 | 9,398-9,693 | 13 |
| Dragonfly | Non-TLS | Predis | 10,614 | ±286 | 2.7% | 🟡 good | 0.094 | ±0.003 | 0.140 | 0.168 | 10,455-10,772 | 13 |
| Dragonfly | TLS | Predis | 7,515 | ±212 | 2.8% | 🟡 good | 0.133 | ±0.004 | 0.182 | 0.225 | 7,398-7,633 | 13 |
| Valkey | Non-TLS | Predis | 14,786 | ±397 | 2.7% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.128 | 14,566-15,007 | 13 |
| Valkey | TLS | Predis | 10,604 | ±264 | 2.5% | 🟡 good | 0.094 | ±0.002 | 0.144 | 0.171 | 10,458-10,750 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,786 ops/sec
- **Average Performance:** 10,502 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
