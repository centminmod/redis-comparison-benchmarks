# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Memory Bank System

This project uses a structured memory bank system with specialized context files. Always check these files for relevant information before starting work:

- **CLAUDE-activeContext.md** - Current session state, goals, and progress
- **CLAUDE-patterns.md** - Established code patterns and conventions to follow
- **CLAUDE-decisions.md** - Architecture decisions and rationale  
- **CLAUDE-shortcuts.md** - Frequently used commands and workflows
- **CLAUDE-troubleshooting.md** - Common issues and proven solutions
- **CLAUDE-codebase.md** - File structure and key component documentation
- **CLAUDE-temp.md** - temp scratch pad only read it when I reference it

**Important**: Always reference the active context file first to understand what's currently being worked on and maintain session continuity.

## Project Overview

This is a Redis-compatible database benchmarking project that compares performance across Redis, KeyDB, Dragonfly, and Valkey. The project supports **two distinct testing approaches**:

1. **Local Testing**: Via `redis-benchmarks.sh` script for development and local analysis
2. **CI/CD Testing**: Via GitHub Actions workflows for automated, reproducible benchmarks

## Two Testing Approaches

### 1. Local Development Testing (`redis-benchmarks.sh`)

**Purpose**: Quick local development, testing configurations, and manual analysis

#### Key Commands
- **Start containers**: `./redis-benchmarks.sh start`
- **Stop containers**: `./redis-benchmarks.sh stop`
- **Container status**: `./redis-benchmarks.sh status`
- **View logs**: `./redis-benchmarks.sh logs [service_name]`
- **Access container shell**: `./redis-benchmarks.sh shell [service_name]`
- **Full benchmark suite**: `./redis-benchmarks.sh` (runs all tests with 1,2,4,8 threads)
- **Quick benchmark**: `./redis-benchmarks.sh quick` (runs 1-2 thread tests only)
- **Full cleanup**: `./redis-benchmarks.sh cleanup`

#### Configuration
```bash
# Thread configuration
REDIS_IO_THREADS=4 KEYDB_SERVER_THREADS=4 ./redis-benchmarks.sh

# Benchmark parameters  
BENCHMARK_REQUESTS=5000 BENCHMARK_CLIENTS=100 ./redis-benchmarks.sh

# Execution control
CLEANUP=y ./redis-benchmarks.sh  # Auto-cleanup after tests
```

### 2. GitHub Actions CI/CD Testing

**Purpose**: Automated, matrix-based benchmarks with comprehensive result archiving

#### Workflow Files
- **Latest**: `.github/workflows/benchmarks-v6-host-phptests.yml` (includes PHP WordPress tests). This workflow already uses the max 10 Github action workflow input variables allowed. Any other togglable variables would need to be setup as workflow environmental variables instead.
- **Host Network**: `.github/workflows/benchmarks-v5-host.yml` (host networking, matrix strategy)
- **Legacy**: `.github/workflows/benchmarks-v[1-4].yml` (historical versions)

##### Latest Workflow Details: benchmarks-v6-host-phptests.yml

**Overview**: Advanced multi-database benchmarking workflow that tests Redis, KeyDB, Dragonfly, and Valkey performance using both traditional memtier benchmarking and real-world WordPress PHP object cache testing.

**Key Features**:
- **Matrix Strategy**: Dynamically generates thread combinations (1-4 threads) for each database based on configurable maximums
- **Dual Testing Approach**: 
  - Traditional memtier benchmarks: 32 performance tests per thread variant (4 databases × 2 TLS variants × 4 thread counts)
  - PHP WordPress simulation: Real-world cache operations with 13 statistical iterations per database
- **Performance Optimizations**: Host networking, CPU pinning to cores 0-3, disabled persistence for pure performance testing
- **Comprehensive Analysis**: Basic charts (latency avg/P50/P99, ops/sec), advanced visualizations (radar charts, heatmaps, scaling analysis), statistical analysis with confidence intervals
- **Security Testing**: Full TLS support with self-signed certificates for encrypted connection benchmarking
- **Result Management**: Thread-specific archiving (`results/benchmarks-v6-host-{threads}t/`), automated git commits with detailed metadata

**Configurable Parameters**:
- `requests`: Number of requests per thread (default: 5000)
- `clients`: Number of clients per thread (default: 100)
- `pipeline`: Pipeline depth (default: 1)
- `data_size`: Data size in bytes (default: 512)
- `key_maximum`: Maximum key value (default: 3,000,000)
- `intrinsic_latency`: Intrinsic latency test duration (default: 5 seconds)
- Individual thread limits for each database (max_redis_io_threads, max_keydb_server_threads, etc.)

**Execution Time**: ~45-60 minutes per thread variant, generates 50+ charts plus comprehensive reports

##### Host Network Workflow: benchmarks-v5-host.yml
Foundation workflow that introduced host networking and matrix strategy capabilities, serving as the base for v6 enhancements.

##### Legacy Workflows: benchmarks-v[1-4].yml
Historical workflow versions preserved for reference and comparison, representing the evolution of the benchmarking system.

#### Trigger Methods
1. **Manual Dispatch**: GitHub UI → Actions → Select workflow → "Run workflow"
2. **Workflow Dispatch Parameters**:
   - `requests`: Requests per thread (default: 5000)
   - `clients`: Clients per thread (default: 100) 
   - `pipeline`: Pipeline depth (default: 1)
   - `data_size`: Payload size (default: 512 bytes)
   - `max_[database]_threads`: Maximum thread count per database

#### Matrix Strategy
- **Dynamic Matrix Generation**: Workflows automatically generate thread combinations (1→4 threads)
- **Per-Database Thread Limits**: Configure maximum threads per database independently
- **Fail-Fast Disabled**: Individual database failures don't stop entire matrix

## Architecture Overview

### Core Components
1. **Local Script**: `redis-benchmarks.sh` - Docker Compose orchestration for development
2. **GitHub Workflows**: Matrix-based CI/CD with Azure runners (4 vCPU, 16GB RAM)
3. **Docker Configuration**: `docker-compose.yml` with 8 services (4 databases × 2 variants: non-TLS + TLS)
4. **Analysis Pipeline**: Python scripts in `/scripts/` for result processing and visualization

### Database Configuration
- **Thread Settings**: 
  - Local: `REDIS_IO_THREADS`, `KEYDB_SERVER_THREADS`, `DRAGONFLY_PROACTOR_THREADS`, `VALKEY_IO_THREADS`
  - CI/CD: Matrix-generated thread combinations with per-database limits
- **Port Mapping**: Non-TLS (6377-6382), TLS (6390-6393)
- **CPU Pinning**: Containers pinned to CPUs 0-3 via cpuset
- **Network Mode**: Host networking (no NAT overhead)

### Results Processing Pipeline
1. **Raw Output**: memtier_benchmark results in text format
2. **Markdown Conversion**: `scripts/parse_memtier_to_md.py` converts to tables
3. **Aggregation**: `scripts/combine_markdown_results.py` creates combined reports
4. **Visualization**: Multiple chart generators (basic, advanced, heatmaps, radar)
5. **Archiving**: Results stored in `/results/benchmarks-v[X]/` directories

## Working with GitHub Actions

### Adding New Workflow
1. Copy latest workflow file (e.g., `benchmarks-v6-host-phptests.yml`)
2. Update workflow `name` and version numbers
3. Modify matrix parameters as needed
4. Update result archive paths

### Customizing Matrix Strategy
```yaml
# Example: Custom thread combinations
strategy:
  matrix:
    variant: [
      {"threads": 1, "redis_io_threads": 1, "keydb_server_threads": 1},
      {"threads": 2, "redis_io_threads": 2, "keydb_server_threads": 2},
      {"threads": 4, "redis_io_threads": 4, "keydb_server_threads": 4}
    ]
```

### Workflow Result Artifacts
- **Combined Reports**: `combined_all_results[_tls].md`
- **Charts**: `advcharts-*.png`, `latency-*.png`, `ops-*.png`
- **Raw Logs**: Individual database benchmark outputs
- **Archive Structure**: `results/benchmarks-v[X]/` with timestamp

## Configuration Variables

### Local Testing (`redis-benchmarks.sh`)
- `REDIS_IO_THREADS` - Redis I/O thread count (default: CPU count)
- `KEYDB_SERVER_THREADS` - KeyDB server thread count (default: CPU count)  
- `DRAGONFLY_PROACTOR_THREADS` - Dragonfly proactor thread count (default: CPU count)
- `VALKEY_IO_THREADS` - Valkey I/O thread count (default: CPU count)
- `DRAGONFLY_PASSWORD` - Password for Dragonfly TLS authentication (default: testpass)
- `BENCHMARK_REQUESTS` - Requests per thread (default: 2000)
- `BENCHMARK_CLIENTS` - Clients per thread (default: 100)
- `CLEANUP` - Auto-cleanup containers (default: n)

### GitHub Actions
- **Workflow Inputs**: All parameters configurable via GitHub UI
- **Matrix Variables**: Dynamic thread combinations per database
- **Environment Variables**: Include `DRAGONFLY_PASSWORD` for TLS authentication
- **Environment**: Ubuntu 24.04, Azure runners, 4 vCPU, 16GB RAM

## Chart Generation

### Requirements
```bash
pip install pandas matplotlib seaborn numpy
```

### Chart Types

#### 1. Basic Charts
**Scripts**: `scripts/latency-charts.py`, `scripts/opssec-charts.py`
- **Latency Charts**: Bar charts showing Average, P50, and P99 latency across thread counts
  - **Filenames**: `latency-{prefix}-avg-{layout}.png`, `latency-{prefix}-p50-{layout}.png`, `latency-{prefix}-p99-{layout}.png`
  - **Layouts**: `single` (grouped bars), `grid` (2×2 subplots)
- **Operations Charts**: Bar charts showing operations per second throughput
  - **Filenames**: `ops-{prefix}-{layout}.png`
  - **Data**: Sets/Gets/Totals operations across 1-8 thread configurations

#### 2. Advanced Charts  
**Script**: `scripts/benchmark_charts.py`
- **Scaling Analysis**: `advcharts-scaling{-tls}.png` - Line chart showing performance scaling across thread counts
- **Database Comparison**: `advcharts-comparison{-tls}.png` - Grouped bar chart comparing database performance
- **Trade-off Analysis**: `advcharts-tradeoff{-tls}.png` - Scatter plot of latency vs throughput with bubble sizing
- **Cache Efficiency**: `advcharts-cache{-tls}.png` - Dual-panel chart showing hit rates and absolute values
- **Latency Distribution**: `advcharts-latency-dist{-tls}.png` - Line charts comparing average and P99 latency
- **Performance Radar**: `advcharts-radar{-tls}.png` - 2×2 polar radar charts showing normalized performance profiles
- **Performance Heatmap**: `advcharts-heatmap{-tls}.png` - 2×2 heatmap grid with normalized performance scores
- **TLS Comparison**: `advcharts-comparison-stack.png` - Stacked bar chart comparing non-TLS vs TLS performance

#### 3. Matrix Charts
**Scripts**: `scripts/latency-charts-matrix.py`, `scripts/opssec-charts-matrix.py`
- **Same chart types as Basic Charts but with configurable output directories**
- **Purpose**: Multi-thread analysis with flexible result placement for CI/CD workflows
- **Output**: Thread-specific directories (`results/benchmarks-v[X]-{threads}t/`)

#### Chart Filename Patterns
- **TLS Variations**: Non-TLS (no suffix) vs TLS (`-tls` suffix)
- **Layout Options**: `single` (26×10 figure) vs `grid` (18×12 figure) 
- **Prefix Types**: `nonTLS`, `TLS` based on configuration tested
- **Database Coverage**: Redis, KeyDB, Dragonfly, Valkey across 1-8 thread configurations

### Usage
```bash
# Basic charts
python scripts/latency-charts.py combined_results.md nonTLS
python scripts/opssec-charts.py combined_results.md TLS

# Advanced charts  
python scripts/benchmark_charts.py --non-tls --input-dir . --output-dir results/
python scripts/benchmark_charts.py --tls --input-dir . --output-dir results/
```

## File Organization

- **Root**: Main scripts, Docker configs, current results
- **`/.github/workflows/`**: CI/CD workflow definitions
- **`/scripts/`**: Python analysis and chart generation tools
- **`/results/`**: Versioned benchmark archives (auto-generated by workflows)
- **`/charts/`**: Legacy chart storage
- **`/tls/`**: Auto-generated TLS certificates (local testing)
- **`/benchmarklogs/`**: Current run outputs (local testing)

## Workflow Development

### Testing New Workflows
1. **Local Testing**: Use `redis-benchmarks.sh` to validate configuration changes
2. **Branch Testing**: Create feature branch and test workflow dispatch
3. **Matrix Validation**: Verify matrix generation logic in `generate-matrix` job

### Adding New Databases
1. Create `Dockerfile-[newdb]` and `Dockerfile-[newdb]-tls`
2. Update `docker-compose.yml` services
3. Modify workflow matrix generation for new database
4. Update benchmark loops in both script and workflow
5. Add to chart generation scripts

### Result Analysis
- **Local Results**: Available immediately in `./benchmarklogs/` and root directory
- **CI/CD Results**: Downloaded from workflow artifacts or archived in `/results/`
- **Comparison**: Use same analysis scripts for both local and CI/CD results

## Working with Memory Bank Files

When working with Claude Code, always:

1. **Check CLAUDE-activeContext.md first** to understand current session state and continue where you left off
2. **Reference CLAUDE-patterns.md** for established coding conventions and patterns to follow
3. **Consult CLAUDE-decisions.md** for context on architectural choices and their rationale
4. **Use CLAUDE-shortcuts.md** for project-specific commands and workflows
5. **Check CLAUDE-troubleshooting.md** for known issues and proven solutions
6. **Refer to CLAUDE-codebase.md** for file structure and component organization
7. **CLAUDE-temp.md** for temp scratch pad only read it when I reference it

### Memory Bank Integration Workflow

```bash
# Before starting work
cat CLAUDE-activeContext.md    # Understand current session
cat CLAUDE-patterns.md         # Review coding standards

# During development
# Update context with progress and insights

# When encountering issues
grep -i "error_keyword" CLAUDE-troubleshooting.md

# When making architectural decisions
echo "## Decision: [Title]" >> CLAUDE-decisions.md
echo "Date: $(date)" >> CLAUDE-decisions.md
echo "Context: [Why this decision was needed]" >> CLAUDE-decisions.md
echo "Decision: [What was decided]" >> CLAUDE-decisions.md
echo "Rationale: [Why this was the best choice]" >> CLAUDE-decisions.md
```

## Context Management Guidelines

- **Update CLAUDE-activeContext.md** at the start of each development session
- **Document new patterns** in CLAUDE-patterns.md when establishing conventions
- **Record architectural decisions** in CLAUDE-decisions.md with full context and rationale
- **Add troubleshooting solutions** to CLAUDE-troubleshooting.md when resolving issues
- **Maintain CLAUDE-shortcuts.md** with frequently used commands and workflows
- **Keep CLAUDE-codebase.md** current with file structure changes
- **Read CLAUDE-temp.md** - temp scratch pad only read it when I reference it

This memory bank system ensures continuity between sessions and provides comprehensive context for effective development work.

# Important Known Issues

## PHP Redis TLS Connection Issue (FULLY RESOLVED - June 2025)

### Overview

**✅ COMPLETELY RESOLVED (June 2025): All PHP Redis TLS issues have been fully resolved.** All 4 databases (Redis, KeyDB, Dragonfly, Valkey) now work reliably with TLS in PHP tests using both PHPRedis and Predis implementations.

**✅ FINAL STATUS: Critical database name parameter bug fixed.** The root cause was that `connectRedis` calls in both PHPRedis and Predis implementations were missing the database name parameter, causing authentication logic to never trigger for Dragonfly TLS connections.

**✅ DRAGONFLY TLS AUTHENTICATION: Fully implemented and working.** Environment variable-based authentication system using `DRAGONFLY_PASSWORD` ensures TLS compliance and security.

**Historical Context**: The PHP Redis extension previously had documented TLS implementation bugs that affected some Redis-compatible databases in WordPress object cache benchmarking. Through comprehensive debugging and implementation fixes, these issues have been completely resolved.

### Current Status (June 2025)
- **All Databases**: Redis, KeyDB, Dragonfly, Valkey - ✅ Working with TLS
- **All Implementations**: PHPRedis (C extension) and Predis (pure PHP) - ✅ Working with TLS  
- **Authentication**: Dragonfly TLS authentication fully implemented - ✅ Working
- **Performance**: TLS vs non-TLS comparison charts available - ✅ Working
- **Reliability**: Statistical analysis and confidence intervals - ✅ Working

### Solution Implemented (Updated: June 2025)

**Phase 1: TLS Debugging Framework**

Enhanced TLS debugging with 6-stage progressive testing in `connectRedis()` method:

1. Raw SSL socket connection verification
2. Minimal SSL context testing
3. Certificate-based SSL context
4. Full SSL context with all options
5. Alternative TLS versions
6. **Fallback**: Skip command validation (allows connection but tests may still fail)

**Phase 2: TLSv1.2 Forcing (June 2025)**

Implemented TLSv1.2 forcing across all PHP Redis implementations to improve TLS reliability:

**PHPRedis Changes (tests/php/RedisTestBase.php):**

- Added `'crypto_method' => STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT` to all SSL contexts
- Minimal SSL context (line ~839)
- Certificate-based SSL context (line ~861)
- Full SSL context (line ~882)
- Simplified crypto_methods array to only test TLSv1.2 (line ~894)
- Enhanced logging to indicate TLSv1.2 usage throughout connection process

**Predis Changes (tests/php/RedisTestBase-predis.php):**

- Added `'crypto_method' => STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT` to SSL options (line ~256)
- Connection validation already uses SET/GET test instead of PING (resolves serialization issues)
- Enhanced TLS configuration logging to mention TLSv1.2 forcing

### Files Modified (PHP Redis TLS Enhancements)

- `tests/php/RedisTestBase.php`: Lines 788-994 enhanced with comprehensive TLS debugging + TLSv1.2 forcing + Dragonfly authentication
- `tests/php/RedisTestBase-predis.php`: Lines 240-316 updated with TLSv1.2 forcing + SET/GET validation + Dragonfly authentication  
- `Dockerfile-dragonfly-tls-nopass`: Added DRAGONFLY_PASSWORD environment variable and requirepass configuration
- `.github/workflows/benchmarks-v6-host-phptests.yml`: Added DRAGONFLY_PASSWORD environment variable and memtier authentication flags
- Added debugging functions: `debugSSLSocket()`, `tryRedisConnection()`, `debugCertificates()`
- Implemented `$connection_established` flag for proper control flow

### Current Status

- **TLSv1.2 forcing implemented** to eliminate TLS version negotiation issues
- **Predis connection validation fixed** (no more `Response\Status` serialization errors)
- **Dragonfly TLS authentication implemented** (resolves container exit issues)
- Both PHPRedis and Predis now use identical TLS configuration for fair comparison
- ✅ **All 4 databases (Redis, KeyDB, Dragonfly, Valkey) now working with TLS in PHP tests**
- TLSv1.2 forcing has resolved most command execution failures for compatible databases

### Rationale for TLSv1.2 Forcing

- TLSv1.3 introduced significant protocol changes that may cause compatibility issues
- Many Redis implementations are optimized for TLSv1.2
- Eliminates TLS version negotiation complexity
- Provides consistent TLS behavior across all PHP Redis implementations

For detailed troubleshooting information, see CLAUDE-troubleshooting.md.

## PHP Redis Charts Summary Enhancement (June 2025)

### New Feature: Comprehensive Chart Documentation

**Added**: GitHub workflow now automatically generates `php_redis_charts_summary.md` with embedded PNG charts and detailed technical explanations.

**Key Features**:
- **Comprehensive Coverage**: Displays all generated performance charts in organized sections
- **Technical Explanations**: Each chart includes detailed interpretation guidance
- **Educational Content**: Explains metrics, chart types, and performance analysis concepts
- **Collapsible Sections**: Organized by chart categories for easy navigation
- **Chart Availability Detection**: Gracefully handles missing charts with appropriate notifications

**Chart Categories Included**:
1. **Basic Performance Charts**: Latency (avg, P50, P99) and throughput charts
2. **Advanced Analysis Charts**: Scaling, comparison, trade-off, cache efficiency, radar, heatmap charts  
3. **PHP Redis Application Performance**: WordPress-specific statistical analysis charts
4. **Implementation Comparison**: PHPRedis vs Predis comparison charts (when available)

**Generated Location**: 
- Workflow: `./benchmarklogs-{threads}t/php_redis_charts_summary.md`
- Results: `results/benchmarks-v6-host-{threads}t/php_redis_charts_summary.md`

**Benefits**:
- Single comprehensive document for all performance visualizations
- Educational value through technical explanations
- Professional presentation suitable for reports and analysis
- Consistent with existing summary file structure

## Dragonfly TLS Authentication Issue Resolution (June 2025)

### Overview
Dragonfly database has a strict security requirement that when TLS is enabled, an explicit authentication method must be configured. This caused GitHub workflow failures where the Dragonfly TLS container would exit immediately with the error: `"TLS configured but no authentication method is used!"`.

### Technical Details
- **Affected Workflow**: `.github/workflows/benchmarks-v6-host-phptests.yml`
- **Root Cause**: Dragonfly security policy requiring authentication when TLS is enabled
- **Symptom**: Container exits preventing PHP tests from connecting to TLS port 6392
- **Impact**: Complete failure of Dragonfly TLS testing in GitHub Actions

### Solution Implemented (June 2025)

**Environment Variable-Based Authentication System**

Implemented a flexible authentication system using the `DRAGONFLY_PASSWORD` environment variable with "testpass" as the default value.

**Key Components:**

1. **Docker Configuration**: Updated `Dockerfile-dragonfly-tls-nopass` to use `--requirepass=${DRAGONFLY_PASSWORD}`
2. **Workflow Integration**: Added `DRAGONFLY_PASSWORD` environment variable to GitHub Actions
3. **Memtier Benchmark Support**: Added `-a ${DRAGONFLY_PASSWORD}` to all Dragonfly TLS memtier commands
4. **PHP Test Integration**: Added authentication support to both PHPRedis and Predis implementations

### Implementation Details

**Dockerfile Changes (`Dockerfile-dragonfly-tls-nopass`):**
- Added `ENV DRAGONFLY_PASSWORD=testpass` for default password
- Updated CMD to use shell expansion: `--requirepass=${DRAGONFLY_PASSWORD}`
- Changed from array format to shell command for environment variable support

**GitHub Workflow Changes (`.github/workflows/benchmarks-v6-host-phptests.yml`):**
- Added `DRAGONFLY_PASSWORD: "testpass"` to environment variables
- Updated 4 memtier benchmark commands (1, 2, 4, 8 threads) with `-a ${DRAGONFLY_PASSWORD}`

**PHPRedis Integration (`tests/php/RedisTestBase.php`):**
- Added Dragonfly detection in TLS connection method
- Authenticates with `$redis->auth($password)` after TLS connection established
- Reads `DRAGONFLY_PASSWORD` environment variable with fallback to 'testpass'

**Predis Integration (`tests/php/RedisTestBase-predis.php`):**
- Added `'password' => $dragonfly_password` to connection parameters
- Enhanced rediss URI with authentication: `rediss://:password@host:port`
- Supports both Predis connection methods with authentication

### Current Status (Updated: June 2025)

- ✅ **Dragonfly TLS Authentication**: Fully implemented and working
- ✅ **Container Stability**: Dragonfly TLS containers now stay running in GitHub Actions
- ✅ **PHP Test Compatibility**: Both PHPRedis and Predis successfully connect to Dragonfly TLS
- ✅ **Memtier Benchmark Support**: All thread variants working with Dragonfly TLS authentication
- ✅ **Complete Database Coverage**: All 4 databases (Redis, KeyDB, Dragonfly, Valkey) now support TLS in PHP tests

### Final Resolution (June 2025)

**Critical Database Name Parameter Bug Fixed**: The final issue preventing Dragonfly TLS authentication was that both `tests/php/RedisTestBase.php` and `tests/php/RedisTestBase-predis.php` were not passing the database name parameter to the `connectRedis` method calls. This caused the authentication logic to never trigger because the database was identified as "Unknown" instead of "Dragonfly".

**Files Modified**:
- `tests/php/RedisTestBase.php` (lines 460, 471): Added `$db_name` parameter to `connectRedis` calls
- `tests/php/RedisTestBase-predis.php` (lines 502, 514): Added `$db_name` parameter to `connectRedis` calls

**Result**: Dragonfly TLS authentication now works correctly in both PHPRedis and Predis implementations.

### Files Modified (Dragonfly TLS Authentication Fix)

- `Dockerfile-dragonfly-tls-nopass`: Added environment variable and requirepass configuration
- `.github/workflows/benchmarks-v6-host-phptests.yml`: Added environment variable and memtier authentication flags
- `tests/php/RedisTestBase.php`: Added PHPRedis authentication for Dragonfly TLS connections  
- `tests/php/RedisTestBase-predis.php`: Added Predis authentication support for both connection methods

### Benefits

- **Flexible Configuration**: Environment variable allows easy password changes without code modifications
- **Security Compliant**: Satisfies Dragonfly's TLS security requirements
- **Cross-Platform Compatible**: Works with all testing scenarios (local, GitHub Actions, different thread counts)
- **Future-Proof**: Foundation for adding authentication to other databases if needed

## PHP Chart Generation Enhancements (June 2025)

### Enhanced Workflow Chart Generation

**Problem Addressed**: The GitHub workflow `benchmarks-v6-host-phptests.yml` used either/or logic for PHP chart generation, running only one of two chart scripts based on implementation availability.

**Solution Implemented**: Enhanced the workflow to run both chart generation scripts sequentially with comprehensive error handling and logging.

#### Workflow Changes (`.github/workflows/benchmarks-v6-host-phptests.yml`)

**Key Improvements**:

1. **Sequential Execution**: Always runs `php_redis_charts.py` (standard charts), then additionally runs `php_redis_charts_comparison.py` when both implementations are available
2. **Fixed Variable Naming**: Corrected `PHPREDIS_FILES`/`PREDIS_FILES` variable naming bug
3. **Robust Error Handling**: Added `|| { echo "⚠️ Script failed, but continuing..."; }` to prevent one script failure from stopping the workflow
4. **Enhanced Logging**: 
   - Clear section headers with `===` formatting
   - Implementation file count reporting
   - Detailed output summary with file counts
   - Visual indicators using emojis
   - Log file tracking and confirmation

**Before vs After**:
- **Before**: Either `php_redis_charts_comparison.py` OR `php_redis_charts.py` (never both)
- **After**: Always `php_redis_charts.py` + conditionally `php_redis_charts_comparison.py`

### Enhanced Comparison Script Missing Data Handling

**Problem Addressed**: The `php_redis_charts_comparison.py` script couldn't gracefully handle scenarios where one implementation failed TLS tests while the other succeeded.

**Solution Implemented**: Added separated TLS mode comparison functionality with comprehensive missing data handling.

#### Comparison Script Changes (`tests/php/php_redis_charts_comparison.py`)

**New Features**:

1. **Separated TLS Mode Charts**: 
   - `php_redis_implementation_comparison_non_tls.png` - Pure non-TLS comparison
   - `php_redis_implementation_comparison_tls.png` - Pure TLS comparison (when data exists)
   - Maintains original combined chart for backward compatibility

2. **Missing Data Visualization**:
   - "No Data" annotations on charts where implementations are missing
   - Data availability heatmap showing which implementation+database combinations have results
   - Proper NaN handling with visual indicators

3. **Enhanced Data Analysis**:
   - Data availability summary logging
   - Per-implementation statistics reporting
   - Graceful degradation when partial data exists

4. **Improved User Experience**:
   - Clear reporting of what charts were generated
   - Detailed data availability breakdown
   - Visual indicators for missing data scenarios

**Chart Output Examples**:
```
📊 Chart types generated:
  - Combined comparison (original)
  - Separated non-TLS comparison
  - Separated TLS comparison (or ⚠️ TLS comparison skipped if no TLS data)
  - TLS reliability analysis
  - Statistical comparison
  - Summary report
```

#### Use Case Scenarios

**Scenario 1**: Both implementations succeed (non-TLS + TLS)
- ✅ Generates all chart types including complete comparisons

**Scenario 2**: PHPRedis TLS fails, Predis TLS succeeds
- ✅ Non-TLS comparison: PHPRedis vs Predis 
- ✅ TLS comparison: Predis only (with "No Data" annotation for PHPRedis)
- ✅ All other charts with appropriate missing data handling

**Scenario 3**: Only one implementation has any results
- ✅ Standard charts still generated via `php_redis_charts.py`
- ⚠️ Comparison charts skipped with clear explanation

### Benefits

1. **Comprehensive Coverage**: Always get both standard and comparison charts when meaningful
2. **Fault Tolerance**: One script failure doesn't break entire chart generation
3. **Better Debugging**: Enhanced logging helps diagnose issues quickly
4. **Flexible Handling**: Works whether you have complete, partial, or single implementation results
5. **Clear Visualization**: Missing data is clearly indicated rather than shown as confusing zeros

### Testing Recommendations

When running the `benchmarks-v6-host-phptests.yml` workflow:
- Check the workflow logs for the enhanced chart generation section
- Look for both standard and comparison chart outputs in results
- Verify missing data scenarios are handled gracefully with proper annotations

For detailed troubleshooting information, see CLAUDE-troubleshooting.md.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.