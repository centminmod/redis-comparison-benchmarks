# WordPress Object Cache PHP Test Summary - 1 Threads

**Test Configuration:**
- Thread Variant: 1
- Test Duration: 30 seconds
- Redis IO Threads: 1
- KeyDB Server Threads: 1
- Dragonfly Proactor Threads: 1
- Valkey IO Threads: 1

**Test Details:**
- Test Type: WordPress Object Cache simulation
- Operations: 70% reads (GET), 30% writes (SETEX with TTL)
- Key Pattern: WordPress cache groups (posts, terms, users, options, comments)
- TTL Range: 1-24 hours
- Databases Tested: Redis, KeyDB, Dragonfly, Valkey (both non-TLS and TLS)
- Database State: FLUSHALL executed before tests

**Workflow Information:**
- Workflow Run: 9
- Commit SHA: 7edc5bf368559ad925743382fb2f2f9c2939b028
- Run Date: Sat Jun  7 08:38:22 UTC 2025
- Matrix Variant: 1t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
