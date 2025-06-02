#!/bin/bash

# Configuration
MEMTIER_REDIS_TLS='y'
MEMTIER_KEYDB_TLS='y'
MEMTIER_DRAGONFLY_TLS='y'
MEMTIER_VALKEY_TLS='y'
CLEANUP='n'  # Set to 'y' to cleanup containers after benchmarks, 'n' to keep them running
USE_DOCKER_COMPOSE=true
CPUS=$(nproc)

# Port Configuration
REDIS_HOST_PORT=6377        # Changed from 6379 to avoid conflict
KEYDB_HOST_PORT=6380
DRAGONFLY_HOST_PORT=6381
VALKEY_HOST_PORT=6382
REDIS_TLS_HOST_PORT=6390
KEYDB_TLS_HOST_PORT=6391
DRAGONFLY_TLS_HOST_PORT=6392
VALKEY_TLS_HOST_PORT=6393

set -e  # Exit on any error

# Add after the configuration section
get_docker_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "ERROR: Neither docker-compose nor docker compose found" >&2
        exit 1
    fi
}

# Set the compose command globally
COMPOSE_CMD=$(get_docker_compose_cmd)

echo "=================================="
echo "REDIS COMPARISON BENCHMARK SUITE"
echo "Configuration: CLEANUP=$CLEANUP, USE_DOCKER_COMPOSE=$USE_DOCKER_COMPOSE"
echo "Docker Compose Command: $COMPOSE_CMD"
echo "Port Configuration: Redis=${REDIS_HOST_PORT}, KeyDB=${KEYDB_HOST_PORT}, Dragonfly=${DRAGONFLY_HOST_PORT}, Valkey=${VALKEY_HOST_PORT}"
echo "=================================="

# System Information
print_system_info() {
    echo "==== System Information ===="
    echo "Kernel: $(uname -r)"
    echo "CPU Count: $CPUS"
    echo "==== CPU Info ===="
    lscpu
    echo "==== Memory Info ===="
    free -m
    echo "==== Disk Info ===="
    df -hT
}

# Setup directories and certificates
setup_environment() {
    echo "==== Setting Up Environment ===="
    mkdir -p benchmarklogs tls
    
    # Generate SSL certificates (matching GitHub workflow)
    pushd tls
    echo "Generating SSL certificates..."
    
    # CA certificate
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out ca.key
    openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
        -subj "/C=US/ST=Some-State/O=OrganizationName/OU=OrganizationalUnit/CN=CA"
    
    # Server certificate
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out test.key
    openssl req -new -key test.key -out test.csr \
        -subj "/C=US/ST=Some-State/O=OrganizationName/OU=OrganizationalUnit/CN=test.com"
    openssl x509 -req -in test.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out test.crt -days 365
    
    # Client certificate
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out client_priv.pem
    openssl req -new -key client_priv.pem -out client.csr \
        -subj "/C=US/ST=Some-State/O=OrganizationName/OU=OrganizationalUnit/CN=test.server.com"
    openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out client_cert.pem -days 365
    
    ls -lAhrt
    popd
    
    # Copy certificates to main directory
    cp tls/* .
}

# Update configurations
update_configurations() {
    echo "==== Updating Configurations ===="
    
    # Non-TLS configurations
    cat >> redis.conf << EOF
io-threads $CPUS
io-threads-do-reads yes
save ""
appendonly no
EOF

    cat >> keydb.conf << EOF
server-threads $CPUS
io-threads-do-reads yes
save ""
appendonly no
EOF

    cat >> valkey.conf << EOF
io-threads $CPUS
io-threads-do-reads yes
save ""
appendonly no
EOF

    # TLS configurations
    cat >> redis-tls.conf << EOF
io-threads $CPUS
io-threads-do-reads yes
tls-port 6390
tls-cert-file /tls/test.crt
tls-key-file /tls/test.key
tls-ca-cert-file /tls/ca.crt
save ""
appendonly no
EOF

    cat >> keydb-tls.conf << EOF
io-threads $CPUS
io-threads-do-reads yes
tls-port 6391
tls-cert-file /tls/test.crt
tls-key-file /tls/test.key
tls-ca-cert-file /tls/ca.crt
save ""
appendonly no
EOF

    cat >> dragonfly-tls.conf << EOF
--proactor_threads=$CPUS
--port=6392
--tls_cert_file=/tls/test.crt
--tls_key_file=/tls/test.key
--tls_ca_cert_file=/tls/ca.crt
--dbfilename=''
EOF

    cat >> valkey-tls.conf << EOF
io-threads $CPUS
io-threads-do-reads yes
tls-port 6393
tls-cert-file /tls/test.crt
tls-key-file /tls/test.key
tls-ca-cert-file /tls/ca.crt
tls-auth-clients no
save ""
appendonly no
EOF

    # Update Dragonfly Dockerfiles
    sed -i "s|--proactor_threads=2|--proactor_threads=$CPUS|" Dockerfile-dragonfly
    sed -i "s|--proactor_threads=2|--proactor_threads=$CPUS|" Dockerfile-dragonfly-tls
}

# Check container status
check_container_status() {
    local service_name=$1
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        # Check if service is running via docker compose
        if $COMPOSE_CMD ps -q "$service_name" 2>/dev/null | xargs docker inspect --format='{{.State.Running}}' 2>/dev/null | grep -q true; then
            return 0  # Container is running
        else
            return 1  # Container is not running
        fi
    else
        # Check if container is running via docker
        if docker ps --format '{{.Names}}' | grep -q "^${service_name}$"; then
            return 0  # Container is running
        else
            return 1  # Container is not running
        fi
    fi
}

# Check all containers status
check_all_containers_status() {
    echo "==== Checking Container Status ===="
    
    local services=("redis" "keydb" "dragonfly" "valkey" "redis-tls" "keydb-tls" "dragonfly-tls" "valkey-tls")
    local running_count=0
    local total_count=${#services[@]}
    
    for service in "${services[@]}"; do
        if check_container_status "$service"; then
            echo "✅ $service is running"
            ((running_count++))
        else
            echo "❌ $service is not running"
        fi
    done
    
    echo "Status: $running_count/$total_count containers running"
    
    if [ $running_count -eq $total_count ]; then
        echo "ℹ️  All containers are already running"
        return 0  # All running
    elif [ $running_count -gt 0 ]; then
        echo "⚠️  Some containers are running, some are not"
        return 2  # Partial
    else
        echo "ℹ️  No containers are running"
        return 1  # None running
    fi
}

# Docker management functions
build_containers() {
    echo "==== Building Docker Images ===="
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        echo "Building with Docker Compose using: $COMPOSE_CMD"
        $COMPOSE_CMD build --parallel
    else
        echo "Building with Docker..."
        # Original approach
        docker build -t redis:latest -f Dockerfile-redis .
        docker build -t keydb:latest -f Dockerfile-keydb .
        docker build -t dragonfly:latest -f Dockerfile-dragonfly .
        docker build -t valkey:latest -f Dockerfile-valkey .
        docker build -t redis-tls:latest -f Dockerfile-redis-tls .
        docker build -t keydb-tls:latest -f Dockerfile-keydb-tls .
        docker build -t dragonfly-tls:latest -f Dockerfile-dragonfly-tls-nopass .
        docker build -t valkey-tls:latest -f Dockerfile-valkey-tls .
    fi
    
    docker images | grep -E 'redis|keydb|dragonfly|valkey'
}

# Smart container startup
start_containers() {
    echo "==== Managing Container Startup ===="
    
    # Check current status
    check_all_containers_status
    local status=$?
    
    if [ $status -eq 0 ]; then
        echo "ℹ️  All containers already running, skipping startup"
        if [ "$CLEANUP" = [nN] ]; then
            echo "ℹ️  CLEANUP=n: Will reuse existing containers"
            return 0
        else
            echo "⚠️  CLEANUP=y: Will restart containers for fresh state"
            stop_containers
        fi
    elif [ $status -eq 2 ]; then
        echo "⚠️  Partial container state detected"
        if [ "$CLEANUP" = [nN] ]; then
            echo "ℹ️  CLEANUP=n: Starting missing containers only"
        else
            echo "⚠️  CLEANUP=y: Restarting all containers for consistency"
            stop_containers
        fi
    fi
    
    # Restart Docker service if needed
    if [ $status -ne 0 ] || [ "$CLEANUP" = [yY] ]; then
        echo "Restarting Docker service..."
        systemctl restart docker
        sleep 5
    fi
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        echo "Starting containers with Docker Compose using: $COMPOSE_CMD"
        $COMPOSE_CMD up -d
        sleep 30
    else
        echo "Starting containers individually..."
        # Start containers that aren't running
        local services=(
            "redis:redis:${REDIS_HOST_PORT}:6379"
            "keydb:keydb:${KEYDB_HOST_PORT}:6379" 
            "dragonfly:dragonfly:${DRAGONFLY_HOST_PORT}:6379"
            "valkey:valkey:${VALKEY_HOST_PORT}:6379"
            "redis-tls:redis-tls:${REDIS_TLS_HOST_PORT}:6390"
            "keydb-tls:keydb-tls:${KEYDB_TLS_HOST_PORT}:6391"
            "dragonfly-tls:dragonfly-tls:${DRAGONFLY_TLS_HOST_PORT}:6392"
            "valkey-tls:valkey-tls:${VALKEY_TLS_HOST_PORT}:6393"
        )
        
        for service_info in "${services[@]}"; do
            IFS=':' read -r container_name image_name host_port container_port <<< "$service_info"
            
            if ! check_container_status "$container_name"; then
                echo "Starting $container_name..."
                docker run --name "$container_name" -d -p "${host_port}:${container_port}" \
                    --cpuset-cpus="0-3" --ulimit memlock=-1 "${image_name}:latest"
            else
                echo "✅ $container_name already running"
            fi
        done
        sleep 30
    fi
    
    # Final status check
    check_all_containers_status
}

# Stop containers function
stop_containers() {
    echo "==== Stopping Containers ===="
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        echo "Stopping containers with Docker Compose using: $COMPOSE_CMD"
        $COMPOSE_CMD down --remove-orphans
    else
        echo "Stopping individual containers..."
        local services=("redis" "keydb" "dragonfly" "valkey" "redis-tls" "keydb-tls" "dragonfly-tls" "valkey-tls")
        for service in "${services[@]}"; do
            if check_container_status "$service"; then
                echo "Stopping $service..."
                docker stop "$service" 2>/dev/null || true
                docker rm "$service" 2>/dev/null || true
            fi
        done
    fi
}

# CSF Firewall management
manage_csf_firewall() {
    echo "==== Managing CSF Firewall ===="
    
    # Get container IPs and add to CSF
    for service in redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls; do
        if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
            CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $service 2>/dev/null)
            if [ ! -z "$CONTAINER_IP" ]; then
                echo "Adding $service ($CONTAINER_IP) to CSF allow list"
                csf -a $CONTAINER_IP $service || echo "Warning: Could not add $CONTAINER_IP to CSF"
            fi
        fi
    done
}

# Database connectivity tests
test_connectivity() {
    echo "==== Testing Database Connectivity ===="
    
    # Wait a bit more for containers to fully start
    echo "Waiting for databases to initialize..."
    sleep 10
    
    # Non-TLS tests
    echo "Testing Redis..."
    docker exec redis redis-cli -h 127.0.0.1 -p 6379 PING || echo "Redis connection failed"
    
    echo "Testing KeyDB..."
    docker exec keydb redis-cli -h 127.0.0.1 -p 6379 PING || echo "KeyDB connection failed"
    
    echo "Testing Dragonfly..."
    docker exec dragonfly redis-cli -h 127.0.0.1 -p 6379 PING || echo "Dragonfly connection failed"
    
    echo "Testing Valkey..."
    docker exec valkey redis-cli -h 127.0.0.1 -p 6379 PING || echo "Valkey connection failed"
    
    # TLS tests
    if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
        echo "Testing Redis TLS..."
        docker exec redis-tls redis-cli -h 127.0.0.1 -p 6390 --tls --insecure \
            --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING || echo "Redis TLS connection failed"
    fi
    
    if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
        echo "Testing KeyDB TLS..."
        docker exec keydb-tls redis-cli -h 127.0.0.1 -p 6391 --tls --insecure \
            --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING || echo "KeyDB TLS connection failed"
    fi
    
    if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
        echo "Testing Dragonfly TLS..."
        docker exec dragonfly-tls redis-cli -h 127.0.0.1 -p 6392 --insecure \
            --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING || echo "Dragonfly TLS connection failed"
    fi
    
    if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
        echo "Testing Valkey TLS..."
        docker exec valkey-tls redis-cli -h 127.0.0.1 -p 6393 --tls --insecure \
            --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING || echo "Valkey TLS connection failed"
    fi
}

# Display container information for manual testing
show_container_info() {
    echo "=================================="
    echo "CONTAINER INFORMATION FOR TESTING"
    echo "=================================="
    echo ""
    echo "Container Status:"
    docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" | grep -E "(redis|keydb|dragonfly|valkey)"
    echo ""
    echo "Connection Commands:"
    echo "Non-TLS:"
    echo "  Redis:     docker exec -it redis redis-cli -h 127.0.0.1 -p 6379"
    echo "  KeyDB:     docker exec -it keydb redis-cli -h 127.0.0.1 -p 6379"
    echo "  Dragonfly: docker exec -it dragonfly redis-cli -h 127.0.0.1 -p 6379"
    echo "  Valkey:    docker exec -it valkey redis-cli -h 127.0.0.1 -p 6379"
    echo ""
    echo "TLS:"
    echo "  Redis TLS:     docker exec -it redis-tls redis-cli -h 127.0.0.1 -p 6390 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt"
    echo "  KeyDB TLS:     docker exec -it keydb-tls redis-cli -h 127.0.0.1 -p 6391 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt"
    echo "  Dragonfly TLS: docker exec -it dragonfly-tls redis-cli -h 127.0.0.1 -p 6392 --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt"
    echo "  Valkey TLS:    docker exec -it valkey-tls redis-cli -h 127.0.0.1 -p 6393 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt"
    echo ""
    echo "Host Connections:"
    echo "  Redis:     redis-cli -h 127.0.0.1 -p $REDIS_HOST_PORT"
    echo "  KeyDB:     redis-cli -h 127.0.0.1 -p $KEYDB_HOST_PORT"
    echo "  Dragonfly: redis-cli -h 127.0.0.1 -p $DRAGONFLY_HOST_PORT"
    echo "  Valkey:    redis-cli -h 127.0.0.1 -p $VALKEY_HOST_PORT"
    echo ""
    echo "Container Management:"
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        echo "  Stop all:   $COMPOSE_CMD down"
        echo "  Start all:  $COMPOSE_CMD up -d"
        echo "  Logs:       $COMPOSE_CMD logs [service_name]"
        echo "  Status:     $COMPOSE_CMD ps"
    else
        echo "  Stop all:   docker stop redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls"
        echo "  Remove all: docker rm redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls"
        echo "  Logs:       docker logs [container_name]"
    fi
    echo ""
    echo "Manual cleanup when done:"
    echo "  ./redis-benchmark.sh cleanup"
    echo "=================================="
}

# Benchmark execution (matching GitHub workflow style)
run_memtier_benchmark() {
    local host=$1
    local port=$2
    local threads=$3
    local output_file=$4
    local tls_opts=$5
    local cpu_affinity=$6
    
    echo "Running benchmark: $output_file"
    
    local cmd="memtier_benchmark -s $host --ratio=1:15 -p $port --protocol=redis \
        -t $threads --distinct-client-seed --hide-histogram --requests=2000 \
        --clients=100 --pipeline=1 --data-size=384 \
        --key-pattern=G:G --key-minimum=1 --key-maximum=1000000 \
        --key-median=500000 --key-stddev=166667 $tls_opts"
    
    if [ ! -z "$cpu_affinity" ]; then
        cmd="taskset -c $cpu_affinity $cmd"
    fi
    
    eval "$cmd | tee $output_file" || echo "Benchmark failed: $output_file"
}

# Main benchmark execution
run_benchmarks() {
    echo "==== Running Benchmarks ===="
    
    # Define thread configurations and CPU affinities
    declare -A cpu_affinities=(
        [1]="0"
        [2]="0,1"
        [4]="0,1,2,3"
        [8]=""
    )
    
    # Non-TLS benchmarks
    for threads in 1 2 4 8; do
        cpu_affinity=${cpu_affinities[$threads]}
        
        # Redis
        run_memtier_benchmark "127.0.0.1" "$REDIS_HOST_PORT" "$threads" \
            "./benchmarklogs/redis_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
        
        # KeyDB
        run_memtier_benchmark "127.0.0.1" "$KEYDB_HOST_PORT" "$threads" \
            "./benchmarklogs/keydb_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
        
        # Dragonfly
        run_memtier_benchmark "127.0.0.1" "$DRAGONFLY_HOST_PORT" "$threads" \
            "./benchmarklogs/dragonfly_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
        
        # Valkey
        run_memtier_benchmark "127.0.0.1" "$VALKEY_HOST_PORT" "$threads" \
            "./benchmarklogs/valkey_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
    done
    
    # TLS benchmarks
    if [[ "$MEMTIER_REDIS_TLS" = [yY] ]] || [[ "$MEMTIER_KEYDB_TLS" = [yY] ]] || 
       [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]] || [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
        
        for threads in 1 2 4 8; do
            cpu_affinity=${cpu_affinities[$threads]}
            
            if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "$REDIS_TLS_HOST_PORT" "$threads" \
                    "./benchmarklogs/redis_benchmarks_${threads}threads_tls.txt" \
                    "--tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify" \
                    "$cpu_affinity"
            fi
            
            if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "$KEYDB_TLS_HOST_PORT" "$threads" \
                    "./benchmarklogs/keydb_benchmarks_${threads}threads_tls.txt" \
                    "--tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify" \
                    "$cpu_affinity"
            fi
            
            if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "$DRAGONFLY_TLS_HOST_PORT" "$threads" \
                    "./benchmarklogs/dragonfly_benchmarks_${threads}threads_tls.txt" \
                    "--tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt" \
                    "$cpu_affinity"
            fi
            
            if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "$VALKEY_TLS_HOST_PORT" "$threads" \
                    "./benchmarklogs/valkey_benchmarks_${threads}threads_tls.txt" \
                    "--tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify" \
                    "$cpu_affinity"
            fi
        done
    fi
}

# Process results (matching GitHub workflow)
process_results() {
    echo "==== Processing Results ===="
    
    # Convert to markdown
    for db in redis keydb dragonfly valkey; do
        for threads in 1 2 4 8; do
            if [ -f "./benchmarklogs/${db}_benchmarks_${threads}threads.txt" ]; then
                python scripts/parse_memtier_to_md.py \
                    "./benchmarklogs/${db}_benchmarks_${threads}threads.txt" \
                    "$(echo ${db^}) $threads Thread$([ $threads -gt 1 ] && echo 's')"
            fi
            
            # TLS results
            if [ -f "./benchmarklogs/${db}_benchmarks_${threads}threads_tls.txt" ]; then
                python scripts/parse_memtier_to_md.py \
                    "./benchmarklogs/${db}_benchmarks_${threads}threads_tls.txt" \
                    "$(echo ${db^}) TLS $threads Thread$([ $threads -gt 1 ] && echo 's')"
            fi
        done
    done
    
    # Combine results
    for db in redis keydb dragonfly valkey; do
        files=""
        for threads in 1 2 4 8; do
            if [ -f "./benchmarklogs/${db}_benchmarks_${threads}threads.md" ]; then
                files="$files ./benchmarklogs/${db}_benchmarks_${threads}threads.md"
            fi
        done
        if [ ! -z "$files" ]; then
            python scripts/combine_markdown_results.py "$files" "$db"
        fi
        
        # TLS results
        tls_files=""
        for threads in 1 2 4 8; do
            if [ -f "./benchmarklogs/${db}_benchmarks_${threads}threads_tls.md" ]; then
                tls_files="$tls_files ./benchmarklogs/${db}_benchmarks_${threads}threads_tls.md"
            fi
        done
        if [ ! -z "$tls_files" ]; then
            python scripts/combine_markdown_results.py "$tls_files" "${db}-tls"
        fi
    done
    
    # Create final combined files
    cat ./benchmarklogs/combined_*_results.md > ./combined_all_results.md 2>/dev/null || true
    cat ./benchmarklogs/combined_*-tls_results.md > ./combined_all_results_tls.md 2>/dev/null || true
}

# Generate charts
generate_charts() {
    echo "==== Generating Charts ===="
    
    if command -v python3 &> /dev/null && python3 -c "import matplotlib" 2>/dev/null; then
        if [ -f "./combined_all_results.md" ]; then
            python scripts/latency-charts.py combined_all_results.md nonTLS || echo "Chart generation failed"
            python scripts/opssec-charts.py combined_all_results.md nonTLS || echo "Chart generation failed"
        fi
        
        if [ -f "./combined_all_results_tls.md" ]; then
            python scripts/latency-charts.py combined_all_results_tls.md TLS || echo "TLS chart generation failed"
            python scripts/opssec-charts.py combined_all_results_tls.md TLS || echo "TLS chart generation failed"
        fi
    else
        echo "Python3 or matplotlib not available, skipping chart generation"
    fi
}

# Cleanup function (now optional)
cleanup() {
    if [ "$CLEANUP" = [yY] ]; then
        echo "==== Cleaning Up (CLEANUP=y) ===="
        
        if [ "$USE_DOCKER_COMPOSE" = true ]; then
            $COMPOSE_CMD down --remove-orphans
            $COMPOSE_CMD rm -f
        else
            docker stop redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
            docker rm redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
        fi
        
        docker rmi redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
        
        echo "✅ Cleanup completed"
    else
        echo "==== Skipping Cleanup (CLEANUP=n) ===="
        echo "ℹ️  Containers left running for manual testing"
        show_container_info
    fi
}

# Manual cleanup function
manual_cleanup() {
    echo "==== Manual Cleanup ===="
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        $COMPOSE_CMD down --remove-orphans
        $COMPOSE_CMD rm -f
        echo "Docker Compose cleanup completed"
    else
        echo "Stopping and removing containers..."
        docker stop redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
        docker rm redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
    fi
    
    echo "Removing images..."
    docker rmi redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
    
    echo "✅ Manual cleanup completed"
}

# Main execution
main() {
    print_system_info
    setup_environment
    update_configurations
    build_containers
    start_containers
    manage_csf_firewall
    test_connectivity
    run_benchmarks
    process_results
    generate_charts
    cleanup
    
    echo "=================================="
    echo "BENCHMARK PROCESS COMPLETED"
    echo "=================================="
    echo "Results available in:"
    echo "  - ./benchmarklogs/ (individual results)"
    echo "  - ./combined_all_results.md (non-TLS summary)"
    echo "  - ./combined_all_results_tls.md (TLS summary)"
    echo "  - *.png (charts, if generated)"
    
    if [ "$CLEANUP" = [nN] ]; then
        echo ""
        echo "🚀 Containers are still running for your testing!"
        echo "Use './redis-benchmark.sh cleanup' when done"
    fi
}

# Standalone start function
standalone_start() {
    echo "==== Standalone Container Start ===="
    
    # Check if we need to set up environment first
    if [ ! -f "docker-compose.yml" ] && [ "$USE_DOCKER_COMPOSE" = true ]; then
        echo "⚠️  No docker-compose.yml found, setting up environment first..."
        setup_environment
        update_configurations
    fi
    
    # Build containers if images don't exist
    echo "Checking if images exist..."
    local missing_images=false
    local required_images=("redis:latest" "keydb:latest" "dragonfly:latest" "valkey:latest" "redis-tls:latest" "keydb-tls:latest" "dragonfly-tls:latest" "valkey-tls:latest")
    
    for image in "${required_images[@]}"; do
        if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
            echo "❌ Missing image: $image"
            missing_images=true
        else
            echo "✅ Found image: $image"
        fi
    done
    
    if [ "$missing_images" = true ]; then
        echo "Building missing images..."
        build_containers
    else
        echo "All required images exist"
    fi
    
    # Start containers
    start_containers
    manage_csf_firewall
    test_connectivity
    show_container_info
}

# Standalone stop function
standalone_stop() {
    echo "==== Standalone Container Stop ===="
    
    # Check current status first
    check_all_containers_status
    local status=$?
    
    if [ $status -eq 1 ]; then
        echo "ℹ️  No containers are running"
        return 0
    fi
    
    stop_containers
    
    # Verify all containers are stopped
    echo "Verifying containers are stopped..."
    check_all_containers_status
}

# Standalone restart function
standalone_restart() {
    echo "==== Standalone Container Restart ===="
    
    echo "Step 1: Stopping containers..."
    standalone_stop
    
    echo ""
    echo "Step 2: Starting containers..."
    standalone_start
}

# Enhanced build-only function
standalone_build() {
    echo "==== Standalone Container Build ===="
    
    # Set up environment if needed
    if [ ! -f "docker-compose.yml" ] && [ "$USE_DOCKER_COMPOSE" = true ]; then
        echo "Setting up environment for build..."
        setup_environment
        update_configurations
    fi
    
    build_containers
    
    echo ""
    echo "✅ Build completed. Available images:"
    docker images | grep -E 'redis|keydb|dragonfly|valkey' | head -10
}

# Enhanced logs function
show_logs() {
    local service=${1:-""}
    
    echo "==== Container Logs ===="
    
    if [ ! -z "$service" ]; then
        echo "Showing logs for: $service"
        if [ "$USE_DOCKER_COMPOSE" = true ]; then
            $COMPOSE_CMD logs -f "$service"
        else
            docker logs -f "$service"
        fi
    else
        echo "Available containers:"
        local services=("redis" "keydb" "dragonfly" "valkey" "redis-tls" "keydb-tls" "dragonfly-tls" "valkey-tls")
        for service in "${services[@]}"; do
            if check_container_status "$service"; then
                echo "  ✅ $service (running)"
            else
                echo "  ❌ $service (not running)"
            fi
        done
        echo ""
        echo "Usage: $0 logs [service_name]"
        echo "Example: $0 logs redis"
    fi
}

# Container shell access function
container_shell() {
    local service=${1:-""}
    
    if [ -z "$service" ]; then
        echo "Usage: $0 shell [service_name]"
        echo "Available services: redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls"
        return 1
    fi
    
    if check_container_status "$service"; then
        echo "Connecting to $service container..."
        docker exec -it "$service" /bin/bash || docker exec -it "$service" /bin/sh
    else
        echo "❌ Container $service is not running"
        echo "Start it first with: $0 start"
    fi
}

# Quick benchmark function (subset of full benchmarks)
quick_benchmark() {
    echo "==== Quick Benchmark (1 & 2 threads only) ===="
    
    # Check if containers are running
    check_all_containers_status
    local status=$?
    
    if [ $status -eq 1 ]; then
        echo "❌ No containers running. Start them first with: $0 start"
        return 1
    fi
    
    mkdir -p benchmarklogs
    
    # Run quick benchmarks (1 and 2 threads only)
    declare -A cpu_affinities=(
        [1]="0"
        [2]="0,1"
    )
    
    for threads in 1 2; do
        cpu_affinity=${cpu_affinities[$threads]}
        echo "Running $threads thread benchmarks..."
        
        # Non-TLS quick benchmarks
        run_memtier_benchmark "127.0.0.1" "$REDIS_HOST_PORT" "$threads" \
            "./benchmarklogs/redis_quick_${threads}threads.txt" "" "$cpu_affinity"
        
        run_memtier_benchmark "127.0.0.1" "$KEYDB_HOST_PORT" "$threads" \
            "./benchmarklogs/keydb_quick_${threads}threads.txt" "" "$cpu_affinity"
        
        run_memtier_benchmark "127.0.0.1" "$DRAGONFLY_HOST_PORT" "$threads" \
            "./benchmarklogs/dragonfly_quick_${threads}threads.txt" "" "$cpu_affinity"
        
        run_memtier_benchmark "127.0.0.1" "$VALKEY_HOST_PORT" "$threads" \
            "./benchmarklogs/valkey_quick_${threads}threads.txt" "" "$cpu_affinity"
    done
    
    echo "✅ Quick benchmark completed. Results in ./benchmarklogs/"
}

# Handle command line arguments
case "${1:-}" in
    "start")
        standalone_start
        exit 0
        ;;
    "stop")
        standalone_stop
        exit 0
        ;;
    "restart")
        standalone_restart
        exit 0
        ;;
    "build")
        standalone_build
        exit 0
        ;;
    "cleanup")
        manual_cleanup
        exit 0
        ;;
    "status")
        check_all_containers_status
        show_container_info
        exit 0
        ;;
    "logs")
        show_logs "${2:-}"
        exit 0
        ;;
    "shell")
        container_shell "${2:-}"
        exit 0
        ;;
    "quick")
        quick_benchmark
        exit 0
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  (none)     Run full benchmark suite"
        echo "  start      Start all containers (builds if needed)"
        echo "  stop       Stop all containers"
        echo "  restart    Restart all containers"
        echo "  build      Build all container images"
        echo "  status     Show container status and connection info"
        echo "  logs       Show logs for all containers"
        echo "  logs <svc> Show logs for specific service"
        echo "  shell <svc> Open shell in specific container"
        echo "  quick      Run quick benchmark (1-2 threads only)"
        echo "  cleanup    Manually cleanup containers and images"
        echo "  help       Show this help message"
        echo ""
        echo "Services: redis, keydb, dragonfly, valkey, redis-tls, keydb-tls, dragonfly-tls, valkey-tls"
        echo ""
        echo "Configuration variables:"
        echo "  CLEANUP=y|n                    Cleanup containers after benchmarks (default: n)"
        echo "  USE_DOCKER_COMPOSE=true|false Use docker-compose or individual containers"
        echo "  MEMTIER_*_TLS=y|n             Enable/disable TLS testing for each database"
        echo ""
        echo "Port Configuration:"
        echo "  Redis: $REDIS_HOST_PORT, KeyDB: $KEYDB_HOST_PORT, Dragonfly: $DRAGONFLY_HOST_PORT, Valkey: $VALKEY_HOST_PORT"
        echo "  TLS - Redis: $REDIS_TLS_HOST_PORT, KeyDB: $KEYDB_TLS_HOST_PORT, Dragonfly: $DRAGONFLY_TLS_HOST_PORT, Valkey: $VALKEY_TLS_HOST_PORT"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run full benchmarks, keep containers running"
        echo "  $0 start              # Just start containers for testing"
        echo "  $0 status             # Check container status"
        echo "  $0 logs redis         # Show Redis container logs"
        echo "  $0 shell keydb        # Open shell in KeyDB container"
        echo "  $0 quick              # Run quick benchmark"
        echo "  $0 restart            # Restart all containers"
        echo "  $0 stop               # Stop all containers"
        echo "  CLEANUP=y $0          # Run benchmarks, cleanup afterwards"
        echo ""
        echo "Docker Compose Command: $COMPOSE_CMD"
        exit 0
        ;;
    *)
        # Run main function
        main "$@"
        ;;
esac