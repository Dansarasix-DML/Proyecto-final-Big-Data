#!/bin/bash

echo "=== DETENIENDO SISTEMA BDA ==="
echo "------------------------------"

echo "=== Deteniendo Apache Spark 3.5.4 ==="
echo "=== Nodos Workers ==="
/opt/hadoop-3.4.1/spark-3.5.4/sbin/stop-workers.sh

echo "=== Nodo Master ==="
/opt/hadoop-3.4.1/spark-3.5.4/sbin/stop-master.sh

echo "=== Deteniendo YARN ==="
stop-yarn.sh

echo "=== Deteniendo HDFS Hadoop ==="
stop-dfs.sh

echo "=== SISTEMA BDA DETENIDO ==="
