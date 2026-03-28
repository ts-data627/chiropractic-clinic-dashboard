"""
generate.py
-----------
Generates synthetic chiropractic clinic data and saves it as CSV files
for use in the ETL pipeline.

Outputs (written to data/):
    - providers.csv
    - patients.csv
    - appointments.csv
    - billing.csv
"""

import random
import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Reproducibility ---
fake = Faker()
np.random.seed(42)
random.seed(42)

# --- Config ---
NUM_PATIENTS  = 500
NUM_PROVIDERS = 8
NUM_APPTS     = 5000
START_DATE    = datetime(2022, 1, 1)
END_DATE      = datetime(2023, 12, 31)

SERVICE_TYPES = [
    "Initial Exam", "Adjustment", "Therapeutic Exercise",
    "Massage Therapy", "X-Ray", "Re-Examination"
]
INSURANCE_TYPES = ["Medicare", "Medicaid", "Blue Cross", "Aetna", "UnitedHealth", "Self-Pay"]
APPT_STATUSES   = ["completed", "no-show", "cancelled"]
STATUS_WEIGHTS  = [0.78, 0.13, 0.09]

# CPT code lookup: service_type -> (cpt_code, charge_low, charge_high)
CPT_CODES = {
    "Initial Exam":         ("99203", 150.00, 200.00),
    "Adjustment":           ("98940",  60.00,  90.00),
    "Therapeutic Exercise": ("97110",  75.00, 100.00),
    "Massage Therapy":      ("97124",  65.00,  85.00),
    "X-Ray":                ("72100", 120.00, 180.00),
    "Re-Examination":       ("99213", 100.00, 140.00),
}

# Expected reimbursement rate by insurance type
INSURANCE_PAY_RATE = {
    "Medicare":     0.70,
    "Medicaid":     0.55,
    "Blue Cross":   0.80,
    "Aetna":        0.78,
    "UnitedHealth": 0.76,
    "Self-Pay":     0.45,
}


# --- Helpers ---

def random_date(start: datetime, end: datetime) -> datetime:
    """Return a random date between start and end (inclusive)."""
    return start + timedelta(days=random.randint(0, (end - start).days))


# --- Generators ---

def generate_providers(n: int = NUM_PROVIDERS) -> pd.DataFrame:
    """
    Generate a DataFrame of synthetic clinic providers.

    Args:
        n: Number of providers to generate. Defaults to NUM_PROVIDERS.

    Returns:
        DataFrame with columns: provider_id, name, specialty, hire_date.
    """
    logger.info(f"Generating {n} providers...")
    providers = []
    for i in range(1, n + 1):
        providers.append({
            "provider_id": i,
            "name":        fake.name(),
            "specialty":   random.choice(["Chiropractor", "Chiropractic Assistant"]),
            "hire_date":   random_date(datetime(2015, 1, 1), datetime(2021, 12, 31)).date(),
        })
    logger.info(f"Providers generated — {len(providers)} rows")
    return pd.DataFrame(providers)


def generate_patients(n: int = NUM_PATIENTS) -> pd.DataFrame:
    """
    Generate a DataFrame of synthetic clinic patients.

    Args:
        n: Number of patients to generate. Defaults to NUM_PATIENTS.

    Returns:
        DataFrame with columns: patient_id, first_name, last_name, date_of_birth,
        city, state, gender, zip_code, insurance_type, created_at.
    """
    logger.info(f"Generating {n} patients...")
    patients = []
    for i in range(1, n + 1):
        patients.append({
            "patient_id":    i,
            "first_name":    fake.first_name(),
            "last_name":     fake.last_name(),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=85).strftime("%Y-%m-%d"),
            "city":          fake.city(),
            "state":         fake.state_abbr(),
            "gender":        random.choice(["M", "F"]),
            "zip_code":      fake.zipcode(),
            "insurance_type": random.choice(INSURANCE_TYPES),
            "created_at":    random_date(START_DATE, END_DATE).date(),
        })
    logger.info(f"Patients generated — {len(patients)} rows")
    return pd.DataFrame(patients)


def generate_appointments(patients_df: pd.DataFrame, providers_df: pd.DataFrame, n: int = NUM_APPTS) -> pd.DataFrame:
    """
    Generate a DataFrame of synthetic clinic appointments.

    Each appointment is randomly assigned a patient, provider, service type,
    and status using weighted probabilities that reflect realistic clinic patterns.

    Args:
        patients_df:  DataFrame of generated patients.
        providers_df: DataFrame of generated providers.
        n:            Number of appointments to generate. Defaults to NUM_APPTS.

    Returns:
        DataFrame with columns: appt_id, patient_id, provider_id, appt_date,
        service_type, status.
    """
    logger.info(f"Generating {n} appointments...")
    appts = []
    for i in range(1, n + 1):
        patient  = patients_df.sample(1).iloc[0]
        provider = providers_df.sample(1).iloc[0]
        service  = random.choice(SERVICE_TYPES)
        status   = random.choices(APPT_STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        appts.append({
            "appt_id":      i,
            "patient_id":   patient["patient_id"],
            "provider_id":  provider["provider_id"],
            "appt_date":    random_date(START_DATE, END_DATE).date(),
            "service_type": service,
            "status":       status,
        })
    logger.info(f"Appointments generated — {len(appts)} rows")
    return pd.DataFrame(appts)


def generate_billing(appts_df: pd.DataFrame, patients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a DataFrame of billing records for completed appointments only.

    Charge amounts are drawn from per-service CPT code ranges. Paid amounts
    are calculated using per-insurance reimbursement rates. Payment date is
    set 7–45 days after the appointment date to simulate real claim processing.

    Args:
        appts_df:    DataFrame of generated appointments.
        patients_df: DataFrame of generated patients (used to look up insurance type).

    Returns:
        DataFrame with columns: billing_id, appt_id, patient_id, cpt_code,
        service_type, charge_amount, paid_amount, insurance_type, payment_date.
    """
    logger.info("Generating billing records for completed appointments...")
    completed = appts_df[appts_df["status"] == "completed"].copy()
    billing   = []

    for _, appt in completed.iterrows():
        patient            = patients_df[patients_df["patient_id"] == appt["patient_id"]].iloc[0]
        cpt, low, high     = CPT_CODES[appt["service_type"]]
        charge             = round(random.uniform(low, high), 2)
        pay_rate           = INSURANCE_PAY_RATE[patient["insurance_type"]]
        paid               = round(charge * pay_rate, 2)
        payment_date       = appt["appt_date"] + timedelta(days=random.randint(7, 45))

        billing.append({
            "billing_id":    len(billing) + 1,
            "appt_id":       appt["appt_id"],
            "patient_id":    appt["patient_id"],
            "cpt_code":      cpt,
            "service_type":  appt["service_type"],
            "charge_amount": charge,
            "paid_amount":   paid,
            "insurance_type": patient["insurance_type"],
            "payment_date":  payment_date,
        })

    logger.info(f"Billing records generated — {len(billing)} rows (completed appointments only)")
    return pd.DataFrame(billing)


# --- Main ---

if __name__ == "__main__":
    logger.info("Starting synthetic data generation...")

    providers_df    = generate_providers()
    patients_df     = generate_patients()
    appointments_df = generate_appointments(patients_df, providers_df)
    billing_df      = generate_billing(appointments_df, patients_df)

    providers_df.to_csv("data/providers.csv",      index=False)
    patients_df.to_csv("data/patients.csv",         index=False)
    appointments_df.to_csv("data/appointments.csv", index=False)
    billing_df.to_csv("data/billing.csv",           index=False)

    total_rows = len(providers_df) + len(patients_df) + len(appointments_df) + len(billing_df)

    logger.info("Data generation complete.")
    logger.info(f"  Providers:    {len(providers_df)} rows")
    logger.info(f"  Patients:     {len(patients_df)} rows")
    logger.info(f"  Appointments: {len(appointments_df)} rows")
    logger.info(f"  Billing:      {len(billing_df)} rows")
    logger.info(f"  Total:        {total_rows} rows written to data/")
