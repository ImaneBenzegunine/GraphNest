FROM apache/airflow:2.7.3
RUN pip install apache-airflow-providers-apache-spark
# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

# Install system dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \ 
    && rm -rf /var/lib/apt/lists/* 
RUN apt update && \
 	apt-get install -y openjdk-17-jdk && \
	apt-get install -y ant && \
	apt-get clean;
ENV JAVA_HOME /user/lib/jvm/java-17-openjdk-arm64
RUN export JAVA_HOME

# Switch back to airflow user
USER airflow
RUN pip install apache-airflow-providers-apache-spark
# Install Python packages
COPY requirements.txt .
RUN pip install --user -r requirements.txt



# Set Spark environment variables
ENV SPARK_HOME=/usr/local/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow/scripts"

# Dockerfile fix

# FROM apache/airflow:2.7.3-python3.10
# #ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow/scripts"
# USER root
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends openjdk-11-jdk && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# # RUN mkdir -p /opt/airflow/scripts && \
# #     chown -R airflow:airflow /opt/airflow/scripts

# # COPY requirements.txt /requirements.txt
# # COPY ./scripts /opt/airflow/scripts

# # Switch to 'airflow' user before pip install (REQUIRED)
# USER airflow

# # RUN pip install --no-cache-dir \
# #     "neo4j<5.12" \
# #     "pandas<2.0.0" \
# #     "apache-airflow-providers-apache-spark" \
# #     -r /requirements.txt
# # COPY requirements.txt /
# # RUN pip install --no-cache-dir -r /requirements.txt    
# COPY requirements.txt /requirements.txt
# RUN pip install --no-cache-dir -r /requirements.txt
    

