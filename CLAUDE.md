# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
- **Latest**: `.github/workflows/benchmarks-v6-host-phptests.yml` (includes PHP WordPress tests)
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
- `BENCHMARK_REQUESTS` - Requests per thread (default: 2000)
- `BENCHMARK_CLIENTS` - Clients per thread (default: 100)
- `CLEANUP` - Auto-cleanup containers (default: n)

### GitHub Actions
- **Workflow Inputs**: All parameters configurable via GitHub UI
- **Matrix Variables**: Dynamic thread combinations per database
- **Environment**: Ubuntu 24.04, Azure runners, 4 vCPU, 16GB RAM

## Chart Generation

### Requirements
```bash
pip install pandas matplotlib seaborn numpy
```

### Chart Types
1. **Basic Charts**: `scripts/latency-charts.py`, `scripts/opssec-charts.py`
2. **Advanced Charts**: `scripts/benchmark_charts.py` (radar, heatmap, scaling)
3. **Matrix Charts**: `scripts/*-matrix.py` for multi-thread analysis

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