
###  **Full Airflow 2.7 Setup Checklist** (based on your script)
---

###  Setting Up Airflow with Docker

#### 1. Initialize Airflow

```bash
cd airflow
docker-compose up airflow-init
```

#### 2. Start Airflow Services (Open a new terminal)

```bash
docker-compose up
```

#### 3. Monitor Running Containers (Optional)

```bash
docker ps
```

#### 4. Access the Airflow UI

Open your browser and go to:

```
http://localhost:8080
```


---
#### 1. **Install prerequisites**

```bash
sudo apt update && sudo apt install -y python3.10-venv python3-pip libpq-dev postgresql postgresql-contrib
```

#### 2. **Create Airflow project directory and virtual environment**

```bash
mkdir -p ~/airflow && cd ~/airflow
python3 -m venv airflow_env
source airflow_env/bin/activate
```

#### 3. **Install Airflow 2.7 with PostgreSQL support**

You should pin the version to ensure Airflow 2.7 specifically:

```bash
pip install "apache-airflow[postgres]==2.7.*" psycopg2
```

#### 4. **Setup PostgreSQL for Airflow**

```bash
sudo -u postgres psql
# Inside psql shell:
CREATE USER airflow WITH PASSWORD 'user';
CREATE DATABASE airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
\q
```

#### 5. **Configure Airflow**

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
```

Then update `~/airflow/airflow.cfg`:

```bash
sed -i 's|^sql_alchemy_conn =.*|sql_alchemy_conn = postgresql+psycopg2://airflow:Wanrltw1@localhost/airflow|' ~/airflow/airflow.cfg
```

Reinitialize:

```bash
airflow db init
```

#### 6. **Create Airflow Admin User**

```bash
airflow users create \
    --username admin \
    --firstname admin \
    --lastname user \
    --role Admin \
    --email admin@example.com \
    --password user
```

---

###  Optional Improvements

* Add `export AIRFLOW_HOME=~/airflow` to your `~/.bashrc` or `~/.zshrc` to avoid setting it every time.
* Use `pip freeze > requirements.txt` to track your setup dependencies.
* If you want to run the scheduler and webserver:

```bash
airflow scheduler &
airflow webserver --port 8080
```

Let me know if you want a `.sh` script version of all these steps.
