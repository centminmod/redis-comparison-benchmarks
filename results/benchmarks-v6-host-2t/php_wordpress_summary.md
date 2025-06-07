# WordPress Object Cache PHP Test Summary - 2 Threads

**Test Configuration:**
- Thread Variant: 2
- Test Duration: 30 seconds
- Redis IO Threads: 2
- KeyDB Server Threads: 2
- Dragonfly Proactor Threads: 2
- Valkey IO Threads: 2

**Test Details:**
- Test Type: WordPress Object Cache simulation
- Operations: 70% reads (GET), 30% writes (SETEX with TTL)
- Key Pattern: WordPress cache groups (posts, terms, users, options, comments)
- TTL Range: 1-24 hours
- Databases Tested: Redis, KeyDB, Dragonfly, Valkey (both non-TLS and TLS)
- Database State: FLUSHALL executed before tests

**Workflow Information:**
- Workflow Run: 14
- Commit SHA: 974263a21855ec3989a1355cbe0e4c01a74a120e
- Run Date: Sat Jun  7 11:47:40 UTC 2025
- Matrix Variant: 2t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
