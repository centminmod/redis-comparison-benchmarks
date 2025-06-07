# WordPress Object Cache PHP Test Summary - 4 Threads

**Test Configuration:**
- Thread Variant: 4
- Test Duration: 30 seconds
- Redis IO Threads: 4
- KeyDB Server Threads: 4
- Dragonfly Proactor Threads: 4
- Valkey IO Threads: 4

**Test Details:**
- Test Type: WordPress Object Cache simulation
- Operations: 70% reads (GET), 30% writes (SETEX with TTL)
- Key Pattern: WordPress cache groups (posts, terms, users, options, comments)
- TTL Range: 1-24 hours
- Databases Tested: Redis, KeyDB, Dragonfly, Valkey (both non-TLS and TLS)
- Database State: FLUSHALL executed before tests

**Workflow Information:**
- Workflow Run: 20
- Commit SHA: 69e0dca776a43d91fb02d2cda4952387b2018aff
- Run Date: Sat Jun  7 21:41:37 UTC 2025
- Matrix Variant: 4t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
