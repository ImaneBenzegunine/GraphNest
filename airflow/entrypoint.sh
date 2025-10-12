#!/bin/bash
set -e

if [ "$1" = 'master' ]; then
    /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.master.Master
elif [ "$1" = 'worker' ]; then
    /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077
else
    exec "$@"
fi