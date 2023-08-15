#!/bin/bash
cd /home
rm -rf memtier_benchmark
git clone https://github.com/RedisLabs/memtier_benchmark.git

cd memtier_benchmark
make clean
autoreconf -ivf
./configure
make -j$(nproc)
make install