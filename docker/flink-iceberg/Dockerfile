ARG FLINK_VERSION=2.2.0
FROM apache/flink:${FLINK_VERSION}-java21

SHELL ["/bin/bash", "-c"]

ARG ICEBERG_FLINK_RUNTIME_VERSION=2.2
ARG ICEBERG_VERSION=1.12.0
ARG KAFKA_CONNECTOR_VERSION=5.0.0-2.2
ARG HADOOP_VERSION=3.4.2
ARG KAFKA_CLIENT_VERSION=4.2.0

USER flink

WORKDIR /opt/flink

# Iceberg runtime and AWS/S3 support
RUN mkdir -p ./lib/iceberg && \
    cd ./lib/iceberg && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/iceberg/iceberg-flink-runtime-${ICEBERG_FLINK_RUNTIME_VERSION}/${ICEBERG_VERSION}/iceberg-flink-runtime-${ICEBERG_FLINK_RUNTIME_VERSION}-${ICEBERG_VERSION}.jar && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar

RUN mkdir -p ./lib/kafka && \
    cd ./lib/kafka && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-kafka/${KAFKA_CONNECTOR_VERSION}/flink-connector-kafka-${KAFKA_CONNECTOR_VERSION}.jar

RUN mkdir -p ./lib/kafka-client && \
    cd ./lib/kafka-client && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/${KAFKA_CLIENT_VERSION}/kafka-clients-${KAFKA_CLIENT_VERSION}.jar
   
 # Hadoop client API and runtime
RUN mkdir -p ./lib/hadoop && \
    cd ./lib/hadoop && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-client-api/${HADOOP_VERSION}/hadoop-client-api-${HADOOP_VERSION}.jar && \
    curl -fO https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-client-runtime/${HADOOP_VERSION}/hadoop-client-runtime-${HADOOP_VERSION}.jar
