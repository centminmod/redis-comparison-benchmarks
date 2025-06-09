# WordPress Object Cache PHP Test Summary - 3 Threads

**Test Configuration:**
- Thread Variant: 3
- Test Duration: 30 seconds
- Redis IO Threads: 3
- KeyDB Server Threads: 3
- Dragonfly Proactor Threads: 3
- Valkey IO Threads: 3

**Test Details:**
- Test Type: WordPress Object Cache simulation with dual implementation comparison
- Operations: 70% reads (GET), 30% writes (SETEX with TTL)
- Key Pattern: WordPress cache groups (posts, terms, users, options, comments)
- TTL Range: 1-24 hours
- Databases Tested: Redis, KeyDB, Dragonfly, Valkey (both non-TLS and TLS)
- Database State: FLUSHALL executed before tests
- Statistical Iterations: 13 per implementation per database

**Implementation Testing:**
- phpredis: 
  - Status: ✅ Tested
  - Implementation: Redis PHP extension (C-based)
  - Performance: High (native C extension)
  - TLS Support: Known issues with command execution
- Predis: 
  - Status: ✅ Tested
  - Implementation: Pure PHP Redis client
  - Performance: Moderate (pure PHP overhead)
  - TLS Support: Enhanced reliability and SSL context handling

**Workflow Information:**
- Workflow Run: 29
- Commit SHA: 050e830014b4b7f581eacef16ffa5a411a865b6d
- Run Date: Mon Jun  9 00:09:43 UTC 2025
- Matrix Variant: 3t

**Files Generated:**
- phpredis test logs: php_wordpress_test_phpredis.log
- Predis test logs: php_wordpress_test_predis.log
- JSON results: php_results/*.json
- Performance charts: php_redis_*.png
- Implementation comparison charts: php_*comparison*.png
- Comparison report: php_redis_implementation_comparison_report.md
- Summary report: php_redis_benchmark_summary.md
