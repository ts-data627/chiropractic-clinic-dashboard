"""
transform.py
------------
Cleans and standardizes synthetic clinic data prior to loading into PostgreSQL.

Each function accepts a raw DataFrame, applies transformations in place on a copy,
and returns the cleaned DataFrame. An is_valid flag is added to each table to mark
records that failed validation without dropping them.
"""

import logging
from datetime import datetime

import pandas as pd

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def transform_patients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the patients DataFrame.

    Transformations:
        - Strip whitespace and apply title case to name and city fields
        - Uppercase gender and state abbreviations
        - Parse date_of_birth to datetime
        - Derive age from date_of_birth
        - Flag records with future date_of_birth as is_valid=False
        - Add transformed_at audit timestamp

    Args:
        df: Raw patients DataFrame.

    Returns:
        Cleaned and validated patients DataFrame.
    """
    logger.info(f"Transforming patients table — {len(df)} rows incoming")
    df = df.copy()  # never mutate the original

    # --- String normalization ---
    df["first_name"] = df["first_name"].str.strip().str.title()
    df["last_name"]  = df["last_name"].str.strip().str.title()
    df["gender"]     = df["gender"].str.strip().str.upper()
    df["city"]       = df["city"].str.strip().str.title()
    df["state"]      = df["state"].str.strip().str.upper()

    # --- Date standardization ---
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")

    # --- Derived field: age ---
    today    = pd.Timestamp.today()
    df["age"] = ((today - df["date_of_birth"]).dt.days // 365).astype("Int64")

    # --- Validation: flag future dates without dropping ---
    df["is_valid"]        = True
    future_dob_mask       = df["date_of_birth"] > today
    df.loc[future_dob_mask, "is_valid"] = False
    invalid_count         = future_dob_mask.sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} patients have a future date_of_birth — flagged is_valid=False")

    # --- Audit timestamp ---
    df["transformed_at"] = pd.Timestamp.now()

    logger.info(f"Patients transform complete — {len(df)} rows, {df['is_valid'].sum()} valid")
    return df


def transform_providers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the providers DataFrame.

    Transformations:
        - Strip whitespace and apply title case to name and specialty fields
        - Parse hire_date to datetime
        - Flag records with future hire_date as is_valid=False
        - Add transformed_at audit timestamp

    Args:
        df: Raw providers DataFrame.

    Returns:
        Cleaned and validated providers DataFrame.
    """
    logger.info(f"Transforming providers table — {len(df)} rows incoming")
    df    = df.copy()
    today = pd.Timestamp.today()

    # --- String normalization ---
    df["name"]      = df["name"].str.strip().str.title()
    df["specialty"] = df["specialty"].str.strip().str.title()

    # --- Date standardization ---
    df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")

    # --- Validation: flag future hire dates without dropping ---
    df["is_valid"]          = True
    future_hire_mask        = df["hire_date"] > today
    df.loc[future_hire_mask, "is_valid"] = False
    invalid_count           = future_hire_mask.sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} providers have a future hire_date — flagged is_valid=False")

    # --- Audit timestamp ---
    df["transformed_at"] = pd.Timestamp.now()

    logger.info(f"Providers transform complete — {len(df)} rows, {df['is_valid'].sum()} valid")
    return df


def transform_appointments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the appointments DataFrame.

    Transformations:
        - Parse appt_date to datetime
        - Strip whitespace and apply title case to service_type and status
        - Flag records with null required fields as is_valid=False
        - Flag records with unrecognized status values as is_valid=False
        - Add transformed_at audit timestamp

    Args:
        df: Raw appointments DataFrame.

    Returns:
        Cleaned and validated appointments DataFrame.
    """
    logger.info(f"Transforming appointments table — {len(df)} rows incoming")
    df = df.copy()

    # --- Date standardization ---
    df["appt_date"] = pd.to_datetime(df["appt_date"], errors="coerce")

    # --- String normalization ---
    df["service_type"] = df["service_type"].str.strip().str.title()
    df["status"]       = df["status"].str.strip().str.title()

    # --- Validation: null required fields ---
    df["is_valid"]  = True
    null_mask       = df[["patient_id", "provider_id", "appt_date", "status"]].isnull().any(axis=1)
    df.loc[null_mask, "is_valid"] = False

    # --- Validation: unrecognized status values ---
    valid_statuses      = ["Completed", "No-Show", "Cancelled"]
    invalid_status_mask = ~df["status"].isin(valid_statuses)
    df.loc[invalid_status_mask, "is_valid"] = False

    invalid_count = (~df["is_valid"]).sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} appointments flagged is_valid=False")

    # --- Audit timestamp ---
    df["transformed_at"] = pd.Timestamp.now()

    logger.info(f"Appointments transform complete — {len(df)} rows, {df['is_valid'].sum()} valid")
    return df


def transform_billing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the billing DataFrame.

    Transformations:
        - Strip whitespace and apply title case to service_type and insurance_type
        - Parse payment_date to datetime
        - Flag records with non-positive charge amounts as is_valid=False
        - Flag records with negative paid amounts as is_valid=False
        - Flag records where paid amount exceeds charge amount as is_valid=False
        - Add transformed_at audit timestamp

    Args:
        df: Raw billing DataFrame.

    Returns:
        Cleaned and validated billing DataFrame.
    """
    logger.info(f"Transforming billing table — {len(df)} rows incoming")
    df = df.copy()

    # --- String normalization ---
    df["service_type"]   = df["service_type"].str.strip().str.title()
    df["insurance_type"] = df["insurance_type"].str.strip().str.title()

    # --- Date standardization ---
    df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")

    # --- Validation: financial integrity checks ---
    df["is_valid"]         = True
    invalid_charge_mask    = df["charge_amount"] <= 0
    invalid_paid_mask      = df["paid_amount"] < 0
    overpaid_mask          = df["paid_amount"] > df["charge_amount"]

    df.loc[invalid_charge_mask | invalid_paid_mask | overpaid_mask, "is_valid"] = False

    invalid_count = (~df["is_valid"]).sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} billing records flagged is_valid=False")

    # --- Audit timestamp ---
    df["transformed_at"] = pd.Timestamp.now()

    logger.info(f"Billing transform complete — {len(df)} rows, {df['is_valid'].sum()} valid")
    return df


# --- Quick test ---

if __name__ == "__main__":
    logger.info("Running transform smoke test against local CSV files...")

    patients_df     = pd.read_csv("data/patients.csv")
    providers_df    = pd.read_csv("data/providers.csv")
    appointments_df = pd.read_csv("data/appointments.csv")
    billing_df      = pd.read_csv("data/billing.csv")

    transform_patients(patients_df)
    transform_providers(providers_df)
    transform_appointments(appointments_df)
    transform_billing(billing_df)

    logger.info("Smoke test complete.")
