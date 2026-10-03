ARG FLINK_VERSION=2.3
FROM apache/flink:${FLINK_VERSION}-java21

SHELL ["/bin/bash", "-c"]

ARG ICEBERG_FLINK_RUNTIME_VERSION=2.3
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.4.2

USER flink

WORKDIR /opt/flink

# Iceberg runtime and AWS/S3 support
RUN mkdir -p ./lib/iceberg && \
    cd ./lib/iceberg && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/iceberg/iceberg-flink-runtime-${ICEBERG_FLINK_RUNTIME_VERSION}/${ICEBERG_VERSION}/iceberg-flink-runtime-${ICEBERG_FLINK_RUNTIME_VERSION}-${ICEBERG_VERSION}.jar && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar

# Hadoop client API and runtime
RUN mkdir -p ./lib/hadoop && \
    cd ./lib/hadoop && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-client-api/${HADOOP_VERSION}/hadoop-client-api-${HADOOP_VERSION}.jar && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-client-runtime/${HADOOP_VERSION}/hadoop-client-runtime-${HADOOP_VERSION}.jar
