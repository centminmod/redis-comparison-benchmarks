# WordPress Object Cache PHP Test Summary - 1 Threads

**Test Configuration:**
- Thread Variant: 1
- Test Duration: 10 seconds
- Redis IO Threads: 1
- KeyDB Server Threads: 1
- Dragonfly Proactor Threads: 1
- Valkey IO Threads: 1

**Test Details:**
- Test Type: WordPress Object Cache simulation with dual implementation comparison
- Operations: 70% reads (GET), 30% writes (SETEX with TTL)
- Key Pattern: WordPress cache groups (posts, terms, users, options, comments)
- TTL Range: 1-24 hours
- Databases Tested: Redis, KeyDB, Dragonfly, Valkey (both non-TLS and TLS)
- Database State: FLUSHALL executed before tests
- Statistical Iterations: 5 per implementation per database

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
- Workflow Run: 42
- Commit SHA: 94c885cbb9931fdbef165f5bb4fdac99d672af7f
- Run Date: Tue Jun 10 11:02:26 UTC 2025
- Matrix Variant: 1t

**Files Generated:**
- phpredis test logs: php_wordpress_test_phpredis.log
- Predis test logs: php_wordpress_test_predis.log
- JSON results: php_results/*.json
- Performance charts: php_redis_*.png
- Implementation comparison charts: php_*comparison*.png
- Comparison report: php_redis_implementation_comparison_report.md
- Summary report: php_redis_benchmark_summary.md
