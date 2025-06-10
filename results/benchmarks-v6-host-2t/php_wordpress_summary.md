# WordPress Object Cache PHP Test Summary - 2 Threads

**Test Configuration:**
- Thread Variant: 2
- Test Duration: 30 seconds
- Redis IO Threads: 2
- KeyDB Server Threads: 2
- Dragonfly Proactor Threads: 2
- Valkey IO Threads: 2

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
- Workflow Run: 41
- Commit SHA: 18c572d21d3db8c91485449108db6d6386a70f3d
- Run Date: Tue Jun 10 10:15:33 UTC 2025
- Matrix Variant: 2t

**Files Generated:**
- phpredis test logs: php_wordpress_test_phpredis.log
- Predis test logs: php_wordpress_test_predis.log
- JSON results: php_results/*.json
- Performance charts: php_redis_*.png
- Implementation comparison charts: php_*comparison*.png
- Comparison report: php_redis_implementation_comparison_report.md
- Summary report: php_redis_benchmark_summary.md
