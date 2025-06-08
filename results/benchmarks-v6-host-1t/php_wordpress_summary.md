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
- Workflow Run: 23
- Commit SHA: cda8bab2e9aca3cd112617151321882b271cffea
- Run Date: Sun Jun  8 00:21:22 UTC 2025
- Matrix Variant: 1t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
