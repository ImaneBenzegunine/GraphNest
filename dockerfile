FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install pyorient pandas

COPY . .

CMD ["python", "Scripts/GraphQL.py"]
# Dockerfile fix
RUN mkdir -p ${AIRFLOW_HOME} && \
    chown -R airflow:airflow ${AIRFLOW_HOME} && \
    chmod -R 775 ${AIRFLOW_HOME}