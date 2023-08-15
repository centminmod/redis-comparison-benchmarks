[![Benchmark Redis vs KeyDB](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks.yml/badge.svg)](https://github.com/centminmod/redis-comparison-benchmarks/actions/workflows/benchmarks.yml)

# Redis Memtier Benchmarks

| Databases | Type | Ops/sec | Hits/sec | Misses/sec | Avg Latency | p50 Latency | p99 Latency | p99.9 Latency | KB/sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Redis 1 Thread | Sets | 5706.46 | --- | --- | 1.10241 | 0.99100 | 1.95900 | 4.07900 | 2406.80 |
Redis 1 Thread | Gets | 85596.97 | 826.75 | 84770.22 | 1.09486 | 0.99100 | 1.95100 | 3.55100 | 3646.81 |
Redis 1 Thread | Totals | 91303.44 | 826.75 | 84770.22 | 1.09533 | 0.99100 | 1.95100 | 3.59900 | 6053.61 |
Redis 2 Threads | Sets | 8898.39 | --- | --- | 1.41531 | 1.31100 | 2.25500 | 2.78300 | 3753.06 |
Redis 2 Threads | Gets | 133475.85 | 1331.20 | 132144.65 | 1.40604 | 1.30300 | 2.25500 | 3.58300 | 5702.54 |
Redis 2 Threads | Totals | 142374.24 | 1331.20 | 132144.65 | 1.40662 | 1.30300 | 2.25500 | 3.51900 | 9455.60 |
Redis 8 Threads | Sets | 7592.81 | --- | --- | 6.65850 | 6.49500 | 9.21500 | 14.20700 | 3202.41 |
Redis 8 Threads | Gets | 113892.19 | 1126.09 | 112766.10 | 6.57747 | 6.43100 | 8.76700 | 14.46300 | 4862.18 |
Redis 8 Threads | Totals | 121485.00 | 1126.09 | 112766.10 | 6.58254 | 6.43100 | 8.76700 | 14.46300 | 8064.59 |

# KeyDB Memtier Benchmarks

| Databases | Type | Ops/sec | Hits/sec | Misses/sec | Avg Latency | p50 Latency | p99 Latency | p99.9 Latency | KB/sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
KeyDB 1 Thread | Sets | 5947.76 | --- | --- | 1.06011 | 0.98300 | 1.82300 | 4.67100 | 2508.57 |
KeyDB 1 Thread | Gets | 89216.38 | 861.71 | 88354.67 | 1.05024 | 0.98300 | 1.67100 | 3.47100 | 3801.01 |
KeyDB 1 Thread | Totals | 95164.14 | 861.71 | 88354.67 | 1.05086 | 0.98300 | 1.67900 | 3.61500 | 6309.58 |
KeyDB 2 Threads | Sets | 11311.17 | --- | --- | 1.10910 | 0.97500 | 2.20700 | 3.64700 | 4770.69 |
KeyDB 2 Threads | Gets | 169667.52 | 1692.15 | 167975.37 | 1.10304 | 0.97500 | 2.20700 | 3.72700 | 7248.77 |
KeyDB 2 Threads | Totals | 180978.69 | 1692.15 | 167975.37 | 1.10342 | 0.97500 | 2.20700 | 3.71100 | 12019.46 |
KeyDB 8 Threads | Sets | 11824.69 | --- | --- | 4.20102 | 4.12700 | 8.57500 | 12.47900 | 4987.28 |
KeyDB 8 Threads | Gets | 177370.40 | 1753.72 | 175616.68 | 4.14949 | 4.12700 | 8.44700 | 11.96700 | 7572.14 |
KeyDB 8 Threads | Totals | 189195.09 | 1753.72 | 175616.68 | 4.15271 | 4.12700 | 8.44700 | 12.03100 | 12559.42 |

# Dragonfly Memtier Benchmarks

Dragonfly was configured with `--proactor_threads=$(nproc)` which = 12 CPU threads.

| Databases | Type | Ops/sec | Hits/sec | Misses/sec | Avg Latency | p50 Latency | p99 Latency | p99.9 Latency | KB/sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Dragonfly 1 Threads | Sets | 4723.15 | --- | --- | 1.31489 | 0.86300 | 11.26300 | 18.30300 | 1992.07 |
Dragonfly 1 Threads | Gets | 70847.19 | 684.29 | 70162.90 | 1.30760 | 0.86300 | 10.87900 | 17.53500 | 3018.40 |
Dragonfly 1 Threads | Totals | 75570.34 | 684.29 | 70162.90 | 1.30806 | 0.86300 | 10.94300 | 17.66300 | 5010.47 |
Dragonfly 2 Thread | Sets | 8147.44 | --- | --- | 1.55731 | 0.69500 | 12.99100 | 21.37500 | 3436.33 |
Dragonfly 2 Thread | Gets | 122211.58 | 1218.86 | 120992.72 | 1.53052 | 0.68700 | 13.24700 | 21.11900 | 5221.29 |
Dragonfly 2 Thread | Totals | 130359.02 | 1218.86 | 120992.72 | 1.53219 | 0.68700 | 13.24700 | 21.11900 | 8657.62 |
Dragonfly 8 Threads | Sets | 18215.12 | --- | --- | 2.76942 | 2.39900 | 10.36700 | 25.47100 | 7682.56 |
Dragonfly 8 Threads | Gets | 273226.78 | 2701.48 | 270525.30 | 2.74424 | 2.35100 | 10.30300 | 24.83100 | 11664.36 |
Dragonfly 8 Threads | Totals | 291441.90 | 2701.48 | 270525.30 | 2.74581 | 2.35100 | 10.30300 | 24.83100 | 19346.92 |

# Memtier Benchmark Parameters

Test with `1:15` ratio for `SET:GET` so for every SET, 15 GETs and pipeline is disabled with `1` as simulating performance for PHP utilization of Redis, KeyDB and Dragonfly.

```
memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_1threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_1threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 1 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_1threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_2threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_2threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 2 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_2threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/redis_benchmarks_8threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/keydb_benchmarks_8threads.txt

memtier_benchmark -s IPADDRESS --ratio=1:15 -p 6379 --protocol=redis -t 8 --distinct-client-seed --hide-histogram --requests=2000 --clients=100 --pipeline=1 --data-size=384 | tee ./benchmarklogs/dragonfly_benchmarks_8threads.txt
```

# Test System

* Intel Xeon E-2276G
* 32GB ECC Memory
* 2x 960GB NVMe Raid 1
* AlmaLinux 8.8 with 4.18 Linux Kernel
* Centmin Mod 130.00beta01 LEMP stack

```
lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              12
On-line CPU(s) list: 0-11
Thread(s) per core:  2
Core(s) per socket:  6
Socket(s):           1
NUMA node(s):        1
Vendor ID:           GenuineIntel
BIOS Vendor ID:      Intel(R) Corporation
CPU family:          6
Model:               158
Model name:          Intel(R) Xeon(R) E-2276G CPU @ 3.80GHz
BIOS Model name:     Intel(R) Xeon(R) E-2276G CPU @ 3.80GHz
Stepping:            10
CPU MHz:             4689.751
CPU max MHz:         4900.0000
CPU min MHz:         800.0000
BogoMIPS:            7584.00
Virtualization:      VT-x
L1d cache:           32K
L1i cache:           32K
L2 cache:            256K
L3 cache:            12288K
NUMA node0 CPU(s):   0-11
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid mpx rdseed adx smap clflushopt intel_pt xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp md_clear flush_l1d arch_capabilities
```
```
free -mlt
              total        used        free      shared  buff/cache   available
Mem:          31812       10911        9859        1369       11041       19079
Low:          31812       21952        9859
High:             0           0           0
Swap:          4090           1        4089
Total:        35903       10912       13949
```