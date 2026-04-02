# Chiropractic Clinic ETL Pipeline & Dashboard

A production-style ETL pipeline that generates synthetic chiropractic clinic data, transforms and validates it with Python, loads it into a PostgreSQL database hosted on AWS RDS, and visualizes it through an interactive Streamlit dashboard.

## Status
Live and operational

## What It Does

Generates a realistic synthetic dataset modeled after a chiropractic clinic's operational data — patients, providers, appointments, and billing records. Built to demonstrate healthcare data engineering patterns using a domain I know firsthand as a practicing chiropractor.

Pipeline flow:
```
generate.py → data/*.csv
            → transform.py → cleaned DataFrames
                           → load.py → AWS RDS (PostgreSQL)
                                     → app.py → Streamlit Dashboard
```

## Tech Stack
- Python 3.x
- Pandas
- Faker
- SQLAlchemy
- psycopg2
- PostgreSQL (AWS RDS)
- Streamlit

## Project Structure
```
chiropractic-clinic-dashboard/
├── generate.py      # Generates synthetic clinic data and saves to CSV
├── transform.py     # Cleans, validates, and standardizes all four tables
├── load.py          # Loads transformed data into PostgreSQL on AWS RDS
├── app.py           # Streamlit dashboard — connects to RDS and visualizes data
└── sql/             # Business-driven analytics queries against the loaded dataset
```

## Setup

**1. Clone the repo**
```
git clone https://github.com/ts-data627/chiropractic-clinic-dashboard.git
cd chiropractic-clinic-dashboard
```

**2. Install dependencies**
```
pip install pandas faker sqlalchemy psycopg2-binary streamlit plotly python-dotenv
```

**3. Set environment variables in a `.env` file**
```
DB_HOST=your-rds-endpoint.us-east-1.rds.amazonaws.com
DB_NAME=healthcare_records
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

## Running the Pipeline
```
# Step 1 — Generate
python generate.py

# Step 2 — Transform
python transform.py

# Step 3 — Load
python load.py

# Step 4 — Launch dashboard
streamlit run app.py
```

## Output
- 9,409 rows across 4 tables (500 patients, 8 providers, 5,000 appointments, 3,901 billing records)
- Synthetic data modeled after real clinic operations with realistic distributions
- Data loaded into PostgreSQL on AWS RDS

## Key Features
- Synthetic data generation with reproducible random seed
- Anomaly flagging on invalid records — no silent drops
- Type-specific data cleaning (dates, strings, categoricals, financials)
- Data validation with logged warnings on quality issues
- Bulk inserts with chunked loading for performance
- Credentials managed via `.env` — no hardcoded secrets
- Interactive Streamlit dashboard connected directly to live RDS data

## SQL Analytics

The `/sql` folder contains 7 queries that answer business questions about provider performance, patient demographics, appointment trends, and billing collection rates.

## Dashboard

`app.py` connects directly to AWS RDS and visualizes key clinic metrics including patient age distribution, new patient acquisition by month, and no-show rates by provider.

## Author

Tevin Sellers | [GitHub](https://github.com/ts-data627) | [LinkedIn](https://www.linkedin.com/in/tevin-s-ba030512b/)
