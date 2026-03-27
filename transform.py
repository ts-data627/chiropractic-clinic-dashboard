"""
transform.py
Cleans & transforms generated patient data for loading into PostgreSQL.
"""

import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def transform_patients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the patients DataFrame.
    
    Transformations:
    - Normalize string fields (strip whitespace, title case names)
    - Standardize date formats
    - Validate and flag anomalies (negative ages, future birthdates)
    - Add audit column: transformed_at
    
    Returns cleaned DataFrame.
    """
    logger.info(f"Transforming patients table — {len(df)} rows incoming")
    
    df = df.copy()  # never mutate the original

    # --- String normalization ---
    df["first_name"] = df["first_name"].str.strip().str.title()
    df["last_name"] = df["last_name"].str.strip().str.title()
    df["gender"] = df["gender"].str.strip().str.upper()
    df["city"] = df["city"].str.strip().str.title()
    df["state"] = df["state"].str.strip().str.upper()

    # --- Date standardization ---
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")

    # --- Derived field: age ---
    today = pd.Timestamp.today()
    df["age"] = ((today - df["date_of_birth"]).dt.days // 365).astype("Int64")

    # --- Anomaly flagging (don't drop — flag and let the load layer decide) ---
    df["is_valid"] = True
    future_dob_mask = df["date_of_birth"] > today
    df.loc[future_dob_mask, "is_valid"] = False
    invalid_count = future_dob_mask.sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} patients have future date_of_birth — flagged is_valid=False")

    # --- Audit column ---
    df["transformed_at"] = pd.Timestamp.now()

    logger.info(f"Patients transform complete — {len(df)} rows, {df['is_valid'].sum()} valid")
    return df

def transform_providers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the providers dataframe."""

    logger.info(f"Transforming providers data. {len(df)} rows incoming.")

    df = df.copy()
    today = pd.Timestamp.today()

    # --- String Normalization ---
    df["name"] = df["name"].str.strip().str.title()
    df["specialty"] = df["specialty"].str.strip().str.title()

    # --- Date Normalization ---
    df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")

    df["is_valid"] = True
    future_hire_mask = df["hire_date"] > today
    df.loc[future_hire_mask, "is_valid"] = False
    invalid_count = future_hire_mask.sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} providers have future date_of_birth — flagged is_valid=False")

    logger.info(f"Providers transform complete - {len(df)} rows, {df['is_valid'].sum()} valid")
    return df

def transform_appointments(df: pd.DataFrame) -> pd.DataFrame:
    """Clean & standardize the appointments dataframe"""

    logger.info(f"Transform appointments data. {len(df)} rows incoming.")

    df = df.copy()

    df["appt_date"] = pd.to_datetime(df["appt_date"], errors="coerce")

    df["service_type"] = df["service_type"].str.strip().str.title()
    df["status"] = df["status"].str.strip().str.title()

    # --- Audit column ---
    df["transformed_at"] = pd.Timestamp.now()

    df["is_valid"] = True
    null_mask = df[["patient_id", "provider_id", "appt_date", "status"]].isnull().any(axis=1)
    df.loc[null_mask, "is_valid"] = False

    valid_statuses = ["Completed", "No-Show", "Cancelled"]
    invalid_status_mask = ~df["status"].isin(valid_statuses)
    df.loc[invalid_status_mask, "is_valid"] = False

    invalid_count = (~df["is_valid"]).sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} appointments flagged is_valid=False")
    
        # --- Audit column ---
    df["transformed_at"] = pd.Timestamp.now()
    
    logger.info(f"Appointments transform complete - {len(df)} rows, {df['is_valid'].sum()} valid")
    return df


def transform_billing(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans & Standardizes Billing data"""
    logger.info(f"Transforms billing data. {len(df)} rows incoming.")

    df = df.copy()

    df["service_type"] = df["service_type"].str.strip().str.title()
    df["insurance_type"] = df["insurance_type"].str.strip().str.title()

    df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")

    # --- Audit column ---
    df["transformed_at"] = pd.Timestamp.now()

    df["is_valid"] = True

    invalid_charge_mask = df["charge_amount"] <= 0
    invalid_paid_mask = df["paid_amount"] < 0
    overpaid_mask = df["paid_amount"] > df["charge_amount"]

    df.loc[invalid_charge_mask | invalid_paid_mask | overpaid_mask, "is_valid"] = False

    invalid_count = (~df["is_valid"]).sum()
    if invalid_count > 0:
        logger.warning(f"{invalid_count} billing records flagged is_valid=False")

    logger.info(f"Billing transform complete. - {len(df)} rows out.")
    return df

# TEST
if __name__ == "__main__":
    patients_df = pd.read_csv("data/patients.csv")
    providers_df = pd.read_csv("data/providers.csv")
    appointments_df = pd.read_csv("data/appointments.csv")
    billing_df = pd.read_csv("data/billing.csv")

    transform_patients(patients_df)
    transform_providers(providers_df)
    transform_appointments(appointments_df)
    transform_billing(billing_df)
