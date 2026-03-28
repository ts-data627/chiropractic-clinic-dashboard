"""
load.py
-------
Orchestrates the full ETL pipeline for the chiropractic clinic dataset.

Reads raw CSV files from data/, applies transformations via transform.py,
and loads the cleaned DataFrames into PostgreSQL tables on AWS RDS.

Tables loaded (in dependency order):
    1. providers
    2. patients
    3. appointments
    4. billing

Database connection is configured via environment variables (see .env).
"""

import os
import logging
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from transform import (
    transform_appointments,
    transform_billing,
    transform_patients,
    transform_providers,
)

# --- Environment and logging setup ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Database config (from environment variables) ---
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST',     'localhost'),
    'database': os.environ.get('DB_NAME',     'chiropractic_data'),
    'user':     os.environ.get('DB_USER',     'postgres'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'port':     os.environ.get('DB_PORT',     '5432'),
}


# --- Connection ---

def get_engine():
    """
    Build and return a SQLAlchemy engine using DB_CONFIG values.

    Returns:
        SQLAlchemy Engine connected to the configured PostgreSQL database.
    """
    url = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(url)


# --- Loaders ---

def load_providers(providers_df: pd.DataFrame, engine) -> None:
    """
    Load the providers DataFrame into the providers table.

    Args:
        providers_df: Cleaned providers DataFrame from transform_providers().
        engine:       SQLAlchemy engine connected to the target database.

    Raises:
        Exception: Re-raises any database error after logging it.
    """
    try:
        logger.info("Loading providers table...")
        providers_df.to_sql(
            'providers',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=500
        )
        logger.info(f"Inserted {len(providers_df)} rows into providers")

        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM providers;")).scalar()
            logger.info(f"Total rows in providers: {total}")

    except Exception as e:
        logger.error(f"Failed to load providers: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")


def load_patients(patients_df: pd.DataFrame, engine) -> None:
    """
    Load the patients DataFrame into the patients table.

    Args:
        patients_df: Cleaned patients DataFrame from transform_patients().
        engine:      SQLAlchemy engine connected to the target database.

    Raises:
        Exception: Re-raises any database error after logging it.
    """
    try:
        logger.info("Loading patients table...")
        patients_df.to_sql(
            'patients',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=500
        )
        logger.info(f"Inserted {len(patients_df)} rows into patients")

        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM patients;")).scalar()
            logger.info(f"Total rows in patients: {total}")

    except Exception as e:
        logger.error(f"Failed to load patients: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")


def load_appointments(appointments_df: pd.DataFrame, engine) -> None:
    """
    Load the appointments DataFrame into the appointments table.

    Args:
        appointments_df: Cleaned appointments DataFrame from transform_appointments().
        engine:          SQLAlchemy engine connected to the target database.

    Raises:
        Exception: Re-raises any database error after logging it.
    """
    try:
        logger.info("Loading appointments table...")
        appointments_df.to_sql(
            'appointments',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=500
        )
        logger.info(f"Inserted {len(appointments_df)} rows into appointments")

        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM appointments;")).scalar()
            logger.info(f"Total rows in appointments: {total}")

    except Exception as e:
        logger.error(f"Failed to load appointments: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")


def load_billing(billing_df: pd.DataFrame, engine) -> None:
    """
    Load the billing DataFrame into the billing table.

    Args:
        billing_df: Cleaned billing DataFrame from transform_billing().
        engine:     SQLAlchemy engine connected to the target database.

    Raises:
        Exception: Re-raises any database error after logging it.
    """
    try:
        logger.info("Loading billing table...")
        billing_df.to_sql(
            'billing',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=500
        )
        logger.info(f"Inserted {len(billing_df)} rows into billing")

        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM billing;")).scalar()
            logger.info(f"Total rows in billing: {total}")

    except Exception as e:
        logger.error(f"Failed to load billing: {e}")
        raise

    finally:
        engine.dispose()
        logger.info("Database connection closed")


# --- Pipeline orchestration ---

def main():
    """
    Run the full ETL pipeline.

    Steps:
        1. Read raw CSV files from data/
        2. Apply transformations via transform.py
        3. Load each table into PostgreSQL in dependency order
        4. Log total pipeline runtime
    """
    start_time = datetime.now()
    logger.info(f"Pipeline starting at {start_time}")

    engine = get_engine()

    # --- Extract ---
    logger.info("Reading CSV files from data/...")
    patients_df     = pd.read_csv("data/patients.csv")
    providers_df    = pd.read_csv("data/providers.csv")
    appointments_df = pd.read_csv("data/appointments.csv")
    billing_df      = pd.read_csv("data/billing.csv")

    # --- Transform ---
    logger.info("Applying transformations...")
    patients_df     = transform_patients(patients_df)
    providers_df    = transform_providers(providers_df)
    appointments_df = transform_appointments(appointments_df)
    billing_df      = transform_billing(billing_df)

    # --- Load (providers and patients before appointments and billing) ---
    load_providers(providers_df, engine)
    load_patients(patients_df, engine)
    load_appointments(appointments_df, engine)
    load_billing(billing_df, engine)

    end_time = datetime.now()
    logger.info(f"Pipeline complete at {end_time}")
    logger.info(f"Total runtime: {end_time - start_time}")


if __name__ == "__main__":
    main()
