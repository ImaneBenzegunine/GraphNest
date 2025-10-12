# Job Recommendation Engine Neo4j— In Progress

##  Project Goal
**Build a graph-based job recommendation system** that:
- Matches candidates to jobs based on skill compatibility
- Recommends career paths using employment history graphs
- Identifies skill gaps for career advancement
- Visualizes professional networks and opportunities

##  Key Features
| Feature | Description | Technology Used |
|---------|-------------|-----------------|
| Skill Matching | Recommends jobs based on skill overlap between candidates and positions | Neo4j Graph Queries |
| Career Pathing | Suggests progression paths using historical employment patterns | NetworkX + GDS Algorithms |
| Gap Analysis | Identifies missing skills for target positions | Spark ML |
| Real-time Dashboard | Interactive visualization of recommendations | Streamlit |



##  Tech Stack

| Component          | Technology               |
|--------------------|--------------------------|
| Database           | Neo4j          |
| Data Generation    | Python Faker, NetworkX   |
| ETL                | Apache Spark   |
| Orchestration      | Airflow                  |
| Visualization      | Streamlit, Metabase      |
| Containerization   | Docker                   |

##  Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.8+


---

### 📦 Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/ImaneBenzegunine/GraphNest.git
cd GraphNest
```

#### 2. Start OrientDB with Docker

```bash
docker-compose up -d
```

---

### Set Up Python Environment

#### 3. Create and Activate Virtual Environment (Windows)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 5. Run the Main Script

```bash
python Script.py
```
