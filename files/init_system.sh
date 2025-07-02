#!/bin/bash

echo "=== INICIANDO SISTEMA BDA ==="
echo "-----------------------------"

echo "=== Iniciando HDFS Hadoop ==="
start-dfs.sh

echo "=== Iniciando YARN ==="
start-yarn.sh

echo "=== Iniciando Apache Spark 3.5.4 ==="
echo "=== Nodo Master ==="
/opt/hadoop-3.4.1/spark-3.5.4/sbin/start-master.sh

echo "=== Nodos Workers ==="
/opt/hadoop-3.4.1/spark-3.5.4/sbin/start-workers.sh

echo "=== SISTEMA BDA INICIADO ==="
