#!/bin/bash

# Configuration
MEMTIER_REDIS_TLS='y'
MEMTIER_KEYDB_TLS='y'
MEMTIER_DRAGONFLY_TLS='y'
MEMTIER_VALKEY_TLS='y'
CPUS=$(nproc)
USE_DOCKER_COMPOSE=true

set -e  # Exit on any error

echo "=================================="
echo "REDIS COMPARISON BENCHMARK SUITE"
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

# Docker management functions
build_containers() {
    echo "==== Building Docker Images ===="
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        docker-compose build --parallel
    else
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

start_containers() {
    echo "==== Starting Containers ===="
    
    # Restart Docker service
    systemctl restart docker
    sleep 5
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        docker-compose up -d
        sleep 30
    else
        # Original approach with improved error handling
        docker run --name redis -d -p 6379:6379 --cpuset-cpus="0-3" --ulimit memlock=-1 redis:latest
        docker run --name keydb -d -p 6380:6379 --cpuset-cpus="0-3" --ulimit memlock=-1 keydb:latest
        docker run --name dragonfly -d -p 6381:6379 --cpuset-cpus="0-3" --ulimit memlock=-1 dragonfly:latest
        docker run --name valkey -d -p 6382:6379 --cpuset-cpus="0-3" --ulimit memlock=-1 valkey:latest
        docker run --name redis-tls -d -p 6390:6390 --cpuset-cpus="0-3" --ulimit memlock=-1 redis-tls:latest
        docker run --name keydb-tls -d -p 6391:6391 --cpuset-cpus="0-3" --ulimit memlock=-1 keydb-tls:latest
        docker run --name dragonfly-tls -d -p 6392:6392 --cpuset-cpus="0-3" --ulimit memlock=-1 dragonfly-tls:latest
        docker run --name valkey-tls -d -p 6393:6393 --cpuset-cpus="0-3" --ulimit memlock=-1 valkey-tls:latest
        sleep 30
    fi
}

# CSF Firewall management
manage_csf_firewall() {
    echo "==== Managing CSF Firewall ===="
    
    # Get container IPs and add to CSF
    for service in redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls; do
        if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
            CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $service)
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
        run_memtier_benchmark "127.0.0.1" "6379" "$threads" \
            "./benchmarklogs/redis_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
        
        # KeyDB
        run_memtier_benchmark "127.0.0.1" "6380" "$threads" \
            "./benchmarklogs/keydb_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
        
        # Dragonfly
        run_memtier_benchmark "127.0.0.1" "6381" "$threads" \
            "./benchmarklogs/dragonfly_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
        
        # Valkey
        run_memtier_benchmark "127.0.0.1" "6382" "$threads" \
            "./benchmarklogs/valkey_benchmarks_${threads}threads.txt" "" "$cpu_affinity"
    done
    
    # TLS benchmarks
    if [[ "$MEMTIER_REDIS_TLS" = [yY] ]] || [[ "$MEMTIER_KEYDB_TLS" = [yY] ]] || 
       [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]] || [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
        
        for threads in 1 2 4 8; do
            cpu_affinity=${cpu_affinities[$threads]}
            
            if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "6390" "$threads" \
                    "./benchmarklogs/redis_benchmarks_${threads}threads_tls.txt" \
                    "--tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify" \
                    "$cpu_affinity"
            fi
            
            if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "6391" "$threads" \
                    "./benchmarklogs/keydb_benchmarks_${threads}threads_tls.txt" \
                    "--tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify" \
                    "$cpu_affinity"
            fi
            
            if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "6392" "$threads" \
                    "./benchmarklogs/dragonfly_benchmarks_${threads}threads_tls.txt" \
                    "--tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt" \
                    "$cpu_affinity"
            fi
            
            if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
                run_memtier_benchmark "127.0.0.1" "6393" "$threads" \
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

# Cleanup function
cleanup() {
    echo "==== Cleaning Up ===="
    
    if [ "$USE_DOCKER_COMPOSE" = true ]; then
        docker-compose down --remove-orphans
        docker-compose rm -f
    else
        docker stop redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
        docker rm redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
    fi
    
    docker rmi redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls 2>/dev/null || true
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
}

# Run main function
main "$@"