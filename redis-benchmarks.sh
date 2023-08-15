#!/bin/bash

echo "==== Kernel ===="
uname -r
echo "==== CPU Info ===="
lscpu
echo "==== Memory Info ===="
free -m

# Setup
mkdir -p benchmarklogs /tls

# git clone
rm -rf redis-comparison-benchmarks
git clone https://github.com/centminmod/redis-comparison-benchmarks
cd redis-comparison-benchmarks

# Generate SSL certificates for TLS benchmarks
# Generate CA's private key and self-signed certificate
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out ca.key
openssl req -new -x509 -days 365 -key ca.key -out ca.crt -subj "/C=US/ST=Some-State/O=OrganizationName/OU=OrganizationalUnit/CN=CA"
# Generate server's private key and certificate signing request (CSR)
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out test.key
openssl req -new -key test.key -out test.csr -subj "/C=US/ST=Some-State/O=OrganizationName/OU=OrganizationalUnit/CN=test.com"
# Sign the server's CSR with the CA's private key to get the server's certificate
openssl x509 -req -in test.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out test.crt -days 365
# Generate client's private key and CSR
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out client_priv.pem
openssl req -new -key client_priv.pem -out client.csr -subj "/C=US/ST=Some-State/O=OrganizationName/OU=OrganizationalUnit/CN=test.server.com"       
# Sign the client's CSR with the CA's private key to get the client's certificate
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client_cert.pem -days 365
# list certs
ls -lAhrt

# Update configuration files for Redis, KeyDB, and Dragonfly with TLS settings
echo "tls-port 6390" >> redis-tls.conf
echo "tls-cert-file /tls/test.crt" >> redis-tls.conf
echo "tls-key-file /tls/test.key" >> redis-tls.conf
echo "tls-ca-cert-file /tls/ca.crt" >> redis-tls.conf

echo "tls-port 6391" >> keydb-tls.conf
echo "tls-cert-file /tls/test.crt" >> keydb-tls.conf
echo "tls-key-file /tls/test.key" >> keydb-tls.conf
echo "tls-ca-cert-file /tls/ca.crt" >> keydb-tls.conf

echo "tls-port 6392" >> dragonfly-tls.conf
echo "tls-cert-file /tls/test.crt" >> dragonfly-tls.conf
echo "tls-key-file /tls/test.key" >> dragonfly-tls.conf
echo "tls-ca-cert-file /tls/ca.crt" >> dragonfly-tls.conf

# list confs
ls -lAhrt

# Building Docker Images
echo "docker build -t redis:latest -f Dockerfile-redis ."
docker build -t redis:latest -f Dockerfile-redis .
echo "docker build -t keydb:latest -f Dockerfile-keydb ."
docker build -t keydb:latest -f Dockerfile-keydb .
echo "docker build -t dragonfly:latest -f Dockerfile-dragonfly ."
docker build -t dragonfly:latest -f Dockerfile-dragonfly .
echo "docker build -t redis-tls:latest -f Dockerfile-redis-tls ."
docker build -t redis-tls:latest -f Dockerfile-redis-tls .
echo "docker build -t keydb-tls:latest -f Dockerfile-keydb-tls ."
docker build -t keydb-tls:latest -f Dockerfile-keydb-tls .
echo "docker build -t dragonfly-tls:latest -f Dockerfile-dragonfly-tls ."
docker build -t dragonfly-tls:latest -f Dockerfile-dragonfly-tls .
docker images | egrep 'redis|keydb|dragonfly'

# Running Docker containers with some assumed flags
systemctl restart docker
echo "docker run --name redis -d -p 6377:6379 --ulimit memlock=-1 redis:latest"
docker run --name redis -d -p 6377:6379 --ulimit memlock=-1 redis:latest
echo "docker run --name keydb -d -p 6378:6380 --ulimit memlock=-1 keydb:latest"
docker run --name keydb -d -p 6378:6380 --ulimit memlock=-1 keydb:latest
echo "docker run --name dragonfly -d -p 6381:6381 --ulimit memlock=-1 dragonfly:latest"
docker run --name dragonfly -d -p 6381:6381 --ulimit memlock=-1 dragonfly:latest
echo "docker run --name redis-tls -d -p 6390:6390 --ulimit memlock=-1 redis-tls:latest"
docker run --name redis-tls -d -p 6390:6390 --ulimit memlock=-1 redis-tls:latest
echo "docker run --name keydb-tls -d -p 6391:6391 --ulimit memlock=-1 keydb-tls:latest"
docker run --name keydb-tls -d -p 6391:6391 --ulimit memlock=-1 keydb-tls:latest
echo "docker run --name dragonfly-tls -d -p 6392:6392 --ulimit memlock=-1 dragonfly-tls:latest"
docker run --name dragonfly-tls -d -p 6392:6392 --ulimit memlock=-1 dragonfly-tls:latest
sleep 20

# PING check
echo "docker exec redis redis-cli -h 127.0.0.1 -p 6379 PING"
docker exec redis redis-cli -h 127.0.0.1 -p 6379 PING
echo "docker exec keydb keydb-cli -h 127.0.0.1 -p 6379 PING"
docker exec keydb keydb-cli -h 127.0.0.1 -p 6379 PING
echo "docker exec dragonfly redis-cli -h 127.0.0.1 -p 6379 PING"
docker exec dragonfly redis-cli -h 127.0.0.1 -p 6379 PING
echo "docker exec redis-tls redis-cli -h 127.0.0.1 -p 6390 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
docker exec redis-tls redis-cli -h 127.0.0.1 -p 6390 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
echo "docker exec keydb-tls keydb-cli -h 127.0.0.1 -p 6391 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
docker exec keydb-tls keydb-cli -h 127.0.0.1 -p 6391 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
# echo "docker exec dragonfly-tls redis-cli -h 127.0.0.1 -p 6392 --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
# docker exec dragonfly-tls redis-cli -h 127.0.0.1 -p 6392 --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING

# Memtier Benchmarks for Redis, KeyDB, Dragonfly
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6377 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_1threads.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6378 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_1threads.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6381 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_1threads.txt

memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6377 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_2threads.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6378 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_2threads.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6381 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_2threads.txt

memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6377 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_8threads.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6378 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_8threads.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6381 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_8threads.txt

# Memtier Benchmarks for Redis, KeyDB, Dragonfly with TLS
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_1threads_tls.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_1threads_tls.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_1threads_tls.txt

memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_2threads_tls.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_2threads_tls.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_2threads_tls.txt

memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_8threads_tls.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_8threads_tls.txt
memtier_benchmark -s 127.0.0.1 --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_8threads_tls.txt

# Convert txt results to markdown
python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_1threads.txt "Redis 1 Thread"
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_1threads.txt "KeyDB 1 Thread"
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_1threads.txt "Dragonfly 1 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_2threads.txt "Redis 2 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_2threads.txt "KeyDB 2 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_2threads.txt "Dragonfly 2 Thread"
python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_8threads.txt "Redis 8 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_8threads.txt "KeyDB 8 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_8threads.txt "Dragonfly 8 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_1threads_tls.txt "Redis TLS 1 Thread"
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_1threads_tls.txt "KeyDB TLS 1 Thread"
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_1threads_tls.txt "Dragonfly TLS 1 Thread"
python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_2threads_tls.txt "Redis TLS 2 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_2threads_tls.txt "KeyDB TLS 2 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_2threads_tls.txt "Dragonfly TLS 2 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_8threads_tls.txt "Redis TLS 8 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_8threads_tls.txt "KeyDB TLS 8 Threads"
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_8threads_tls.txt "Dragonfly TLS 8 Threads"

# Combine Redis Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/redis_benchmarks_1threads.md ./benchmarklogs/redis_benchmarks_2threads.md ./benchmarklogs/redis_benchmarks_8threads.md" redis
cat ./benchmarklogs/combined_redis_results.md

# Combine KeyDB Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/keydb_benchmarks_1threads.md ./benchmarklogs/keydb_benchmarks_2threads.md ./benchmarklogs/keydb_benchmarks_8threads.md" keydb
cat ./benchmarklogs/combined_keydb_results.md

# Combine Dragonfly Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/dragonfly_benchmarks_1threads.md ./benchmarklogs/dragonfly_benchmarks_2threads.md ./benchmarklogs/dragonfly_benchmarks_8threads.md" dragonfly
cat ./benchmarklogs/combined_dragonfly_results.md

# Combine Redis TLS Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/redis_benchmarks_1threads_tls.md ./benchmarklogs/redis_benchmarks_2threads_tls.md ./benchmarklogs/redis_benchmarks_8threads_tls.md" "redis-tls"
cat ./benchmarklogs/combined_redis-tls_results.md

# Combine KeyDB TLS Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/keydb_benchmarks_1threads_tls.md ./benchmarklogs/keydb_benchmarks_2threads_tls.md ./benchmarklogs/keydb_benchmarks_8threads_tls.md" "keydb-tls"
cat ./benchmarklogs/combined_keydb-tls_results.md

# Combine Dragonfly TLS Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/dragonfly_benchmarks_1threads_tls.md ./benchmarklogs/dragonfly_benchmarks_2threads_tls.md ./benchmarklogs/dragonfly_benchmarks_8threads_tls.md" "dragonfly-tls"
cat ./benchmarklogs/combined_dragonfly-tls_results.md

# Cleanup
docker stop redis keydb dragonfly redis-tls keydb-tls dragonfly-tls
docker rm redis keydb dragonfly redis-tls keydb-tls dragonfly-tls

echo "Benchmarking process completed."
