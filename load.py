import os
import logging
import pandas as pd 
from datetime import datetime
from sqlalchemy import create_engine, text
from transform import transform_appointments, transform_billing, transform_patients, transform_providers

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host':     os.environ.get('DB_HOST',     'localhost'),
    'database': os.environ.get('DB_NAME',    'chiropractic_data'),
    'user':     os.environ.get('DB_USER',     'postgres'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'port':     os.environ.get('DB_PORT',     '5432'),
}


def get_engine():
    """Create and return a SQLAlchemy engine using environment variables."""
    url = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(url)

def load_providers(providers_df, engine):
    try:
        logger.info("Connecting to PostgreSQL...")
        providers_df.to_sql(
           'providers',
           engine,
           if_exists='append',
           index=False,
           method='multi',
           chunksize=500 
        )
        logger.info(f"Successfully inserted {len(providers_df)} rows into providers")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM providers;"))
            total = result.scalar()
            logger.info(f"Total rows now in providers: {total}")

    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")

def load_patients(patients_df, engine):
    try:
        logger.info("Connecting to PostgreSQL...")
        patients_df.to_sql(
            'patients',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=500
        )
        logger.info(f"Successfully inserted {len(patients_df)} rows into patients")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM patients;"))
            total = result.scalar()
            logger.info(f"Total rows now in patients: {total}")

    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")

def load_appointments(appointments_df, engine):
    try:
        logger.info("Connecting to Postgres...")
        appointments_df.to_sql(
            'appointments',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=500
        )
        logger.info(f"Successfully inserted {len(appointments_df)} rows into appointments")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM appointments;"))
            total = result.scalar()
            logger.info(f"Total rows now in appointments: {total}")

    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")

def load_billing(billing_df, engine):
    try:
        logger.info("Connecting to Postgres...")
        billing_df.to_sql(
            'billing',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=500
        )
        logger.info(f"Successfully inserted {len(billing_df)} rows into billing")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM billing"))
            total = result.scalar()
            logger.info(f"Total rows now in billing: {total}")

    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")


def main():
    start_time = datetime.now()
    logging.info(f"Starting pipeline at {start_time}")
    engine = get_engine()

    patients_df = pd.read_csv("data/patients.csv")
    providers_df = pd.read_csv("data/providers.csv")
    appointments_df = pd.read_csv("data/appointments.csv")
    billing_df = pd.read_csv("data/billing.csv")

    patients_df = transform_patients(patients_df)
    providers_df = transform_providers(providers_df)
    appointments_df = transform_appointments(appointments_df)
    billing_df = transform_billing(billing_df)

    load_patients(patients_df, engine)
    load_providers(providers_df, engine)
    load_appointments(appointments_df, engine)
    load_billing(billing_df, engine)

    end_time = datetime.now()
    logging.info(f"Pipeline finished at {end_time}")
    logging.info(f"Pipeline finished in {end_time - start_time}")

if __name__ == "__main__":
    main()
