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
- Workflow Run: 12
- Commit SHA: b88801cf1cc13f538278e1e3dfa3194972a62ea6
- Run Date: Sat Jun  7 10:30:39 UTC 2025
- Matrix Variant: 3t

**Files Generated:**
- Raw test logs: php_wordpress_test.log
- JSON results: php_results/*.json
- Charts: php_redis_*.png
- Summary report: php_redis_benchmark_summary.md
