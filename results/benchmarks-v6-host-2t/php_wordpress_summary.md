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
- Workflow Run: 10
- Commit SHA: 0762400a6af84e7b33a4357329281dee56c025ac
- Run Date: Sat Jun  7 09:08:05 UTC 2025
- Matrix Variant: 2t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
