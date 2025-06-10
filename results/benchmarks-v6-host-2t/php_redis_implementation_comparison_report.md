# PHP Redis Implementation Comparison Report

**Generated:** 2025-06-10 11:06:37 UTC

## Implementation Overview

| Implementation | Total Tests | TLS Tests | Non-TLS Tests |
|---|---|---|---|
| predis | 8 | 4 | 4 |
| phpredis | 8 | 4 | 4 |

## Performance Summary

### predis
- **Average Operations/sec:** 9970
- **Average Latency:** 0.104ms
- **TLS Performance Impact:** 26.0%

### phpredis
- **Average Operations/sec:** 11339
- **Average Latency:** 0.091ms
- **TLS Performance Impact:** 21.8%

## TLS Reliability

- **predis TLS Success Rate:** 100.0% (4/4 databases)
- **phpredis TLS Success Rate:** 100.0% (4/4 databases)

## Recommendations

### Performance vs Reliability Trade-offs

- **phpredis** shows 1.1x better performance than Predis

### Use Case Recommendations

- **High Performance, Non-TLS:** Use phpredis for maximum throughput
- **TLS Required:** Use Predis for better SSL reliability
- **Cross-Platform Deployment:** Use Predis for consistency
- **Extension Dependencies:** Use Predis if phpredis installation is challenging
