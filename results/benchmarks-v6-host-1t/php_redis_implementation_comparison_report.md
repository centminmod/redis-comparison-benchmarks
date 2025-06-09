# PHP Redis Implementation Comparison Report

**Generated:** 2025-06-09 07:46:46 UTC

## Implementation Overview

| Implementation | Total Tests | TLS Tests | Non-TLS Tests |
|---|---|---|---|
| predis | 8 | 4 | 4 |
| phpredis | 4 | 0 | 4 |

## Performance Summary

### predis
- **Average Operations/sec:** 11493
- **Average Latency:** 0.090ms
- **TLS Performance Impact:** 26.2%

### phpredis
- **Average Operations/sec:** 14550
- **Average Latency:** 0.070ms

## TLS Reliability

- **predis TLS Success Rate:** 100.0% (4/4 databases)
- **phpredis TLS Success Rate:** 0.0% (0/4 databases)

## Recommendations

### Performance vs Reliability Trade-offs

- **phpredis** shows 1.3x better performance than Predis
- **Predis** shows better TLS reliability (4 vs 0 successful connections)

### Use Case Recommendations

- **High Performance, Non-TLS:** Use phpredis for maximum throughput
- **TLS Required:** Use Predis for better SSL reliability
- **Cross-Platform Deployment:** Use Predis for consistency
- **Extension Dependencies:** Use Predis if phpredis installation is challenging
