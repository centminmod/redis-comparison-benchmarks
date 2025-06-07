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
- Workflow Run: 6
- Commit SHA: 74213e4a7d881c8e7c33e212b4f397180ca4e7c6
- Run Date: Sat Jun  7 05:47:45 UTC 2025
- Matrix Variant: 2t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
