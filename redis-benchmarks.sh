#!/bin/bash
MEMTIER_REDIS_TLS='y'
MEMTIER_KEYDB_TLS='y'
MEMTIER_DRAGONFLY_TLS='y'
MEMTIER_VALKEY_TLS='y'
CPUS=$(nproc)

echo "==== Kernel ===="
uname -r
echo "==== CPU Info ===="
lscpu
echo "==== Memory Info ===="
free -m

# Setup
mkdir -p benchmarklogs /tls

# Generate SSL certificates for TLS benchmarks
# Generate CA's private key and self-signed certificate
pushd /tls
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
popd

# git clone
rm -rf redis-comparison-benchmarks
git clone https://github.com/centminmod/redis-comparison-benchmarks
cd redis-comparison-benchmarks
\cp -af /tls/* .

# Updated config for non-TLS
echo "io-threads $CPUS" >> redis.conf
echo "io-threads-do-reads yes" >> redis.conf

echo "io-threads $CPUS" >> keydb.conf
echo "io-threads-do-reads yes" >> keydb.conf

echo "io-threads $CPUS" >> valkey.conf
echo "io-threads-do-reads yes" >> valkey.conf

# echo "" >> dragonfly.conf

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

echo "tls-port 6393" >> valkey-tls.conf
echo "tls-cert-file /tls/test.crt" >> valkey-tls.conf
echo "tls-key-file /tls/test.key" >> valkey-tls.conf
echo "tls-ca-cert-file /tls/ca.crt" >> valkey-tls.conf
# Valkey also requires these for TLS to work with redis-cli and memtier
echo "tls-auth-clients no" >> valkey-tls.conf

# list confs
ls -lAhrt

# adjust dragonfly --proactor_threads=X
sed -i "s|--proactor_threads=2|--proactor_threads=$(nproc)|" Dockerfile-dragonfly
sed -i "s|--proactor_threads=2|--proactor_threads=$(nproc)|" Dockerfile-dragonfly-tls

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
echo "docker build -t valkey:latest -f Dockerfile-valkey ."
docker build -t valkey:latest -f Dockerfile-valkey .
echo "docker build -t valkey-tls:latest -f Dockerfile-valkey-tls ."
docker build -t valkey-tls:latest -f Dockerfile-valkey-tls .
docker images | egrep 'redis|keydb|dragonfly|valkey'

# Running Docker containers with some assumed flags
systemctl restart docker
echo "docker run --name redis -d -p 6377:6379 --ulimit memlock=-1 redis:latest"
docker run --name redis -d -p 6377:6379 --ulimit memlock=-1 redis:latest
echo "docker run --name keydb -d -p 6378:6379 --ulimit memlock=-1 keydb:latest"
docker run --name keydb -d -p 6378:6379 --ulimit memlock=-1 keydb:latest
echo "docker run --name dragonfly -d -p 6381:6381 --ulimit memlock=-1 dragonfly:latest"
docker run --name dragonfly -d -p 6381:6381 --ulimit memlock=-1 dragonfly:latest
echo "docker run --name redis-tls -d -p 6390:6390 --ulimit memlock=-1 redis-tls:latest"
docker run --name redis-tls -d -p 6390:6390 --ulimit memlock=-1 redis-tls:latest
echo "docker run --name keydb-tls -d -p 6391:6391 --ulimit memlock=-1 keydb-tls:latest"
docker run --name keydb-tls -d -p 6391:6391 --ulimit memlock=-1 keydb-tls:latest
echo "docker run --name dragonfly-tls -d -p 6392:6392 --ulimit memlock=-1 dragonfly-tls:latest"
docker run --name dragonfly-tls -d -p 6392:6392 --ulimit memlock=-1 dragonfly-tls:latest
echo "docker run --name valkey -d -p 6382:6379 --ulimit memlock=-1 valkey:latest"
docker run --name valkey -d -p 6382:6379 --ulimit memlock=-1 valkey:latest
echo "docker run --name valkey-tls -d -p 6393:6393 --ulimit memlock=-1 valkey-tls:latest"
docker run --name valkey-tls -d -p 6393:6393 --ulimit memlock=-1 valkey-tls:latest
sleep 20

# Get docker IP
REDIS_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis)
echo $REDIS_CONTAINER_IP
csf -a $REDIS_CONTAINER_IP redis

KEYDB_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' keydb)
echo $KEYDB_CONTAINER_IP
csf -a $KEYDB_CONTAINER_IP keydb

DRAGONFLY_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dragonfly)
echo $DRAGONFLY_CONTAINER_IP
csf -a $DRAGONFLY_CONTAINER_IP dragonfly

REDIS_TLS_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis-tls)
echo $REDIS_TLS_CONTAINER_IP
csf -a $REDIS_TLS_CONTAINER_IP redis-tls

KEYDB_TLS_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' keydb-tls)
echo $KEYDB_TLS_CONTAINER_IP
csf -a $KEYDB_TLS_CONTAINER_IP keydb-tls

DRAGONFLY_TLS_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dragonfly-tls)
echo $DRAGONFLY_TLS_CONTAINER_IP
csf -a $DRAGONFLY_TLS_CONTAINER_IP dragonfly-tls

VALKEY_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' valkey)
echo $VALKEY_CONTAINER_IP
csf -a $VALKEY_CONTAINER_IP valkey

VALKEY_TLS_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' valkey-tls)
echo $VALKEY_TLS_CONTAINER_IP
csf -a $VALKEY_TLS_CONTAINER_IP valkey-tls

# PING check
# docker restart redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls
# echo "docker exec redis redis-cli -h 127.0.0.1 -p 6379 PING"
# docker exec redis redis-cli -h 127.0.0.1 -p 6379 PING
# echo "docker exec keydb keydb-cli -h 127.0.0.1 -p 6379 PING"
# docker exec keydb keydb-cli -h 127.0.0.1 -p 6379 PING
# echo "docker exec dragonfly redis-cli -h 127.0.0.1 -p 6379 PING"
# docker exec dragonfly redis-cli -h 127.0.0.1 -p 6379 PING
# echo "docker exec redis-tls redis-cli -h 127.0.0.1 -p 6390 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
# docker exec redis-tls redis-cli -h 127.0.0.1 -p 6390 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
# echo "docker exec keydb-tls keydb-cli -h 127.0.0.1 -p 6391 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
# docker exec keydb-tls keydb-cli -h 127.0.0.1 -p 6391 --tls --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
# echo "docker exec dragonfly-tls redis-cli -h 127.0.0.1 -p 6392 --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
# docker exec dragonfly-tls redis-cli -h 127.0.0.1 -p 6392 --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
docker restart redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls
echo "redis-cli -h $REDIS_CONTAINER_IP -p 6379 PING"
redis-cli -h $REDIS_CONTAINER_IP -p 6379 PING
echo "redis-cli -h $KEYDB_CONTAINER_IP -p 6379 PING"
redis-cli -h $KEYDB_CONTAINER_IP -p 6379 PING
echo "redis-cli -h $DRAGONFLY_CONTAINER_IP -p 6379 PING"
redis-cli -h $DRAGONFLY_CONTAINER_IP -p 6379 PING
echo "redis-cli -h $VALKEY_CONTAINER_IP -p 6379 PING"
redis-cli -h $VALKEY_CONTAINER_IP -p 6379 PING
if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  echo "redis-cli -h $REDIS_TLS_CONTAINER_IP -p 6390 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
  redis-cli -h $REDIS_TLS_CONTAINER_IP -p 6390 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  echo "redis-cli -h $KEYDB_TLS_CONTAINER_IP -p 6391 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
  redis-cli -h $KEYDB_TLS_CONTAINER_IP -p 6391 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  echo "redis-cli -h $DRAGONFLY_TLS_CONTAINER_IP -p 6392 --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt --pass V3ryS3cur3P@sswOrd PING"
  redis-cli -h $DRAGONFLY_TLS_CONTAINER_IP -p 6392 --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt --pass V3ryS3cur3P@sswOrd PING
fi
if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
  echo "redis-cli -h $VALKEY_TLS_CONTAINER_IP -p 6393 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING"
  redis-cli -h $VALKEY_TLS_CONTAINER_IP -p 6393 --tls --insecure --cert /tls/test.crt --key /tls/test.key --cacert /tls/ca.crt PING
fi

# Memtier Benchmarks for Redis, KeyDB, Dragonfly
echo "memtier_benchmark -s \"$REDIS_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_1threads.txt"
memtier_benchmark -s "$REDIS_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_1threads.txt
echo "memtier_benchmark -s \"$KEYDB_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_1threads.txt"
memtier_benchmark -s "$KEYDB_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_1threads.txt
echo "memtier_benchmark -s \"$DRAGONFLY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_1threads.txt"
memtier_benchmark -s "$DRAGONFLY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_1threads.txt
echo "memtier_benchmark -s \"$VALKEY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_1threads.txt"
memtier_benchmark -s "$VALKEY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_1threads.txt
echo "memtier_benchmark -s \"$REDIS_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_2threads.txt"
memtier_benchmark -s "$REDIS_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_2threads.txt
echo "memtier_benchmark -s \"$KEYDB_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_2threads.txt"
memtier_benchmark -s "$KEYDB_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_2threads.txt
echo "memtier_benchmark -s \"$DRAGONFLY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_2threads.txt"
memtier_benchmark -s "$DRAGONFLY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_2threads.txt
echo "memtier_benchmark -s \"$VALKEY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_2threads.txt"
memtier_benchmark -s "$VALKEY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_2threads.txt

echo "memtier_benchmark -s \"$REDIS_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_4threads.txt"
memtier_benchmark -s "$REDIS_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_4threads.txt
echo "memtier_benchmark -s \"$KEYDB_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_4threads.txt"
memtier_benchmark -s "$KEYDB_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_4threads.txt
echo "memtier_benchmark -s \"$DRAGONFLY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_4threads.txt"
memtier_benchmark -s "$DRAGONFLY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_4threads.txt
echo "memtier_benchmark -s \"$VALKEY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_4threads.txt"
memtier_benchmark -s "$VALKEY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_4threads.txt

echo "memtier_benchmark -s \"$REDIS_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_8threads.txt"
memtier_benchmark -s "$REDIS_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_8threads.txt
echo "memtier_benchmark -s \"$KEYDB_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_8threads.txt"
memtier_benchmark -s "$KEYDB_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_8threads.txt
echo "memtier_benchmark -s \"$DRAGONFLY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_8threads.txt"
memtier_benchmark -s "$DRAGONFLY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_8threads.txt
echo "memtier_benchmark -s \"$VALKEY_CONTAINER_IP\" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_8threads.txt"
memtier_benchmark -s "$VALKEY_CONTAINER_IP" --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_8threads.txt
# Memtier Benchmarks for Redis, KeyDB, Dragonfly with TLS
if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$REDIS_TLS_CONTAINER_IP\" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_1threads_tls.txt"
  memtier_benchmark -s "$REDIS_TLS_CONTAINER_IP" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_1threads_tls.txt
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$KEYDB_TLS_CONTAINER_IP\" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_1threads_tls.txt"
  memtier_benchmark -s "$KEYDB_TLS_CONTAINER_IP" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_1threads_tls.txt
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$DRAGONFLY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_1threads_tls.txt"
  memtier_benchmark -s "$DRAGONFLY_TLS_CONTAINER_IP" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_1threads_tls.txt
fi
if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$VALKEY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_1threads_tls.txt"
  memtier_benchmark -s "$VALKEY_TLS_CONTAINER_IP" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_1threads_tls.txt
fi
if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$REDIS_TLS_CONTAINER_IP\" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_2threads_tls.txt"
  memtier_benchmark -s "$REDIS_TLS_CONTAINER_IP" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_2threads_tls.txt
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$KEYDB_TLS_CONTAINER_IP\" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_2threads_tls.txt"
  memtier_benchmark -s "$KEYDB_TLS_CONTAINER_IP" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_2threads_tls.txt
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$DRAGONFLY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_2threads_tls.txt"
  memtier_benchmark -s "$DRAGONFLY_TLS_CONTAINER_IP" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_2threads_tls.txt
fi
if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$VALKEY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_2threads_tls.txt"
  memtier_benchmark -s "$VALKEY_TLS_CONTAINER_IP" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_2threads_tls.txt
fi
if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$REDIS_TLS_CONTAINER_IP\" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_4threads_tls.txt"
  memtier_benchmark -s "$REDIS_TLS_CONTAINER_IP" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_4threads_tls.txt
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$KEYDB_TLS_CONTAINER_IP\" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_4threads_tls.txt"
  memtier_benchmark -s "$KEYDB_TLS_CONTAINER_IP" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_4threads_tls.txt
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$DRAGONFLY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_4threads_tls.txt"
  memtier_benchmark -s "$DRAGONFLY_TLS_CONTAINER_IP" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_4threads_tls.txt
fi
if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$VALKEY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_4threads_tls.txt"
  memtier_benchmark -s "$VALKEY_TLS_CONTAINER_IP" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 4 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_4threads_tls.txt
fi
if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$REDIS_TLS_CONTAINER_IP\" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_8threads_tls.txt"
  memtier_benchmark -s "$REDIS_TLS_CONTAINER_IP" --ratio=1:15 -p 6390 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_8threads_tls.txt
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$KEYDB_TLS_CONTAINER_IP\" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_8threads_tls.txt"
  memtier_benchmark -s "$KEYDB_TLS_CONTAINER_IP" --ratio=1:15 -p 6391 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_8threads_tls.txt
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$DRAGONFLY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_8threads_tls.txt"
  memtier_benchmark -s "$DRAGONFLY_TLS_CONTAINER_IP" --ratio=1:15 -p 6392 --protocol=redis --tls --cert=${PWD}/client_cert.pem --key=${PWD}/client_priv.pem --cacert=${PWD}/ca.crt --password V3ryS3cur3P@sswOrd -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_8threads_tls.txt
fi
if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
  echo "memtier_benchmark -s \"$VALKEY_TLS_CONTAINER_IP\" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_8threads_tls.txt"
  memtier_benchmark -s "$VALKEY_TLS_CONTAINER_IP" --ratio=1:15 -p 6393 --protocol=redis --tls --cert=${PWD}/test.crt --key=${PWD}/test.key --cacert=${PWD}/ca.crt --tls-skip-verify -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/valkey_benchmarks_8threads_tls.txt
fi

# Convert txt results to markdown
python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_1threads.txt "Redis 1 Thread"
cat ./benchmarklogs/redis_benchmarks_1threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_1threads.txt "KeyDB 1 Thread"
cat ./benchmarklogs/keydb_benchmarks_1threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_1threads.txt "Dragonfly 1 Threads"
cat ./benchmarklogs/dragonfly_benchmarks_1threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_1threads.txt "Valkey 1 Thread"
cat ./benchmarklogs/valkey_benchmarks_1threads.md

python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_2threads.txt "Redis 2 Threads"
cat ./benchmarklogs/redis_benchmarks_2threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_2threads.txt "KeyDB 2 Threads"
cat ./benchmarklogs/keydb_benchmarks_2threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_2threads.txt "Dragonfly 2 Threads"
cat ./benchmarklogs/dragonfly_benchmarks_2threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_2threads.txt "Valkey 2 Threads"
cat ./benchmarklogs/valkey_benchmarks_2threads.md

python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_4threads.txt "Redis 4 Threads"
cat ./benchmarklogs/redis_benchmarks_4threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_4threads.txt "KeyDB 4 Threads"
cat ./benchmarklogs/keydb_benchmarks_4threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_4threads.txt "Dragonfly 4 Threads"
cat ./benchmarklogs/dragonfly_benchmarks_4threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_4threads.txt "Valkey 4 Threads"
cat ./benchmarklogs/valkey_benchmarks_4threads.md

python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_8threads.txt "Redis 8 Threads"
cat ./benchmarklogs/redis_benchmarks_8threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_8threads.txt "KeyDB 8 Threads"
cat ./benchmarklogs/keydb_benchmarks_8threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_8threads.txt "Dragonfly 8 Threads"
cat ./benchmarklogs/dragonfly_benchmarks_8threads.md
python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_8threads.txt "Valkey 8 Threads"
cat ./benchmarklogs/valkey_benchmarks_8threads.md

if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_1threads_tls.txt "Redis TLS 1 Thread"
  cat ./benchmarklogs/redis_benchmarks_1threads_tls.md
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_1threads_tls.txt "KeyDB TLS 1 Thread"
  cat ./benchmarklogs/keydb_benchmarks_1threads_tls.md
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_1threads_tls.txt "Dragonfly TLS 1 Thread"
  cat ./benchmarklogs/dragonfly_benchmarks_1threads_tls.md
fi
if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_2threads_tls.txt "Redis TLS 2 Threads"
  cat ./benchmarklogs/redis_benchmarks_2threads_tls.md
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_2threads_tls.txt "KeyDB TLS 2 Threads"
  cat ./benchmarklogs/keydb_benchmarks_2threads_tls.md
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_2threads_tls.txt "Dragonfly TLS 2 Threads"
  cat ./benchmarklogs/dragonfly_benchmarks_2threads_tls.md
fi

if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_4threads_tls.txt "Redis TLS 4 Threads"
  cat ./benchmarklogs/redis_benchmarks_4threads_tls.md
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_4threads_tls.txt "KeyDB TLS 4 Threads"
  cat ./benchmarklogs/keydb_benchmarks_4threads_tls.md
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_4threads_tls.txt "Dragonfly TLS 4 Threads"
  cat ./benchmarklogs/dragonfly_benchmarks_4threads_tls.md
fi

if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/redis_benchmarks_8threads_tls.txt "Redis TLS 8 Threads"
  cat ./benchmarklogs/redis_benchmarks_8threads_tls.md
fi
if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/keydb_benchmarks_8threads_tls.txt "KeyDB TLS 8 Threads"
  cat ./benchmarklogs/keydb_benchmarks_8threads_tls.md
fi
if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/dragonfly_benchmarks_8threads_tls.txt "Dragonfly TLS 8 Threads"
  cat ./benchmarklogs/dragonfly_benchmarks_8threads_tls.md
fi
if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
  python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_1threads_tls.txt "Valkey TLS 1 Thread"
  cat ./benchmarklogs/valkey_benchmarks_1threads_tls.md
  python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_2threads_tls.txt "Valkey TLS 2 Threads"
  cat ./benchmarklogs/valkey_benchmarks_2threads_tls.md
  python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_4threads_tls.txt "Valkey TLS 4 Threads"
  cat ./benchmarklogs/valkey_benchmarks_4threads_tls.md
  python scripts/parse_memtier_to_md.py ./benchmarklogs/valkey_benchmarks_8threads_tls.txt "Valkey TLS 8 Threads"
  cat ./benchmarklogs/valkey_benchmarks_8threads_tls.md
fi

# Combine Redis Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/redis_benchmarks_1threads.md ./benchmarklogs/redis_benchmarks_2threads.md ./benchmarklogs/redis_benchmarks_8threads.md" redis
cat ./benchmarklogs/combined_redis_results.md

# Combine KeyDB Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/keydb_benchmarks_1threads.md ./benchmarklogs/keydb_benchmarks_2threads.md ./benchmarklogs/keydb_benchmarks_4threads.md ./benchmarklogs/keydb_benchmarks_8threads.md" keydb
cat ./benchmarklogs/combined_keydb_results.md

# Combine Dragonfly Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/dragonfly_benchmarks_1threads.md ./benchmarklogs/dragonfly_benchmarks_2threads.md ./benchmarklogs/dragonfly_benchmarks_4threads.md ./benchmarklogs/dragonfly_benchmarks_8threads.md" dragonfly
cat ./benchmarklogs/combined_dragonfly_results.md

# Combine Valkey Benchmark MD Table
python scripts/combine_markdown_results.py "./benchmarklogs/valkey_benchmarks_1threads.md ./benchmarklogs/valkey_benchmarks_2threads.md ./benchmarklogs/valkey_benchmarks_4threads.md ./benchmarklogs/valkey_benchmarks_8threads.md" valkey
cat ./benchmarklogs/combined_valkey_results.md

if [[ "$MEMTIER_REDIS_TLS" = [yY] ]]; then
  # Combine Redis TLS Benchmark MD Table
  python scripts/combine_markdown_results.py "./benchmarklogs/redis_benchmarks_1threads_tls.md ./benchmarklogs/redis_benchmarks_2threads_tls.md ./benchmarklogs/redis_benchmarks_4threads_tls.md ./benchmarklogs/redis_benchmarks_8threads_tls.md" "redis-tls"
  cat ./benchmarklogs/combined_redis-tls_results.md
fi

if [[ "$MEMTIER_KEYDB_TLS" = [yY] ]]; then
  # Combine KeyDB TLS Benchmark MD Table
  python scripts/combine_markdown_results.py "./benchmarklogs/keydb_benchmarks_1threads_tls.md ./benchmarklogs/keydb_benchmarks_2threads_tls.md ./benchmarklogs/keydb_benchmarks_4threads_tls.md ./benchmarklogs/keydb_benchmarks_8threads_tls.md" "keydb-tls"
  cat ./benchmarklogs/combined_keydb-tls_results.md
fi

if [[ "$MEMTIER_DRAGONFLY_TLS" = [yY] ]]; then
  # Combine Dragonfly TLS Benchmark MD Table
  python scripts/combine_markdown_results.py "./benchmarklogs/dragonfly_benchmarks_1threads_tls.md ./benchmarklogs/dragonfly_benchmarks_2threads_tls.md ./benchmarklogs/dragonfly_benchmarks_4threads_tls.md ./benchmarklogs/dragonfly_benchmarks_8threads_tls.md" "dragonfly-tls"
  cat ./benchmarklogs/combined_dragonfly-tls_results.md
fi

if [[ "$MEMTIER_VALKEY_TLS" = [yY] ]]; then
  # Combine Valkey TLS Benchmark MD Table
  python scripts/combine_markdown_results.py "./benchmarklogs/valkey_benchmarks_1threads_tls.md ./benchmarklogs/valkey_benchmarks_2threads_tls.md ./benchmarklogs/valkey_benchmarks_4threads_tls.md ./benchmarklogs/valkey_benchmarks_8threads_tls.md" "valkey-tls"
  cat ./benchmarklogs/combined_valkey-tls_results.md
fi

# Cleanup
docker stop redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls
docker rm redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls
docker rmi redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls

echo "Benchmarking process completed."
