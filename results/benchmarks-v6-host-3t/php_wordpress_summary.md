# WordPress Object Cache PHP Test Summary - 3 Threads

**Test Configuration:**
- Thread Variant: 3
- Test Duration: 30 seconds
- Redis IO Threads: 3
- KeyDB Server Threads: 3
- Dragonfly Proactor Threads: 3
- Valkey IO Threads: 3

**Test Details:**
- Test Type: WordPress Object Cache simulation
- Operations: 70% reads (GET), 30% writes (SETEX with TTL)
- Key Pattern: WordPress cache groups (posts, terms, users, options, comments)
- TTL Range: 1-24 hours
- Databases Tested: Redis, KeyDB, Dragonfly, Valkey (both non-TLS and TLS)
- Database State: FLUSHALL executed before tests

**Workflow Information:**
- Workflow Run: 27
- Commit SHA: 2631b42846c75255110e6c186e5190fb888e8ba7
- Run Date: Sun Jun  8 16:21:41 UTC 2025
- Matrix Variant: 3t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
