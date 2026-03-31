import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

fake = Faker()
np.random.seed(42)
random.seed(42)

# ── CONFIG ──────────────────────────────────────────────────────────────────
NUM_PATIENTS   = 500
NUM_PROVIDERS  = 8
NUM_APPTS      = 5000
START_DATE     = datetime(2022, 1, 1)
END_DATE       = datetime(2023, 12, 31)

SERVICE_TYPES  = [
    "Initial Exam", "Adjustment", "Therapeutic Exercise",
    "Massage Therapy", "X-Ray", "Re-Examination"
]
INSURANCE_TYPES = ["Medicare", "Medicaid", "Blue Cross", "Aetna", "UnitedHealth", "Self-Pay"]
APPT_STATUSES   = ["completed", "no-show", "cancelled"]
STATUS_WEIGHTS  = [0.78, 0.13, 0.09]
CPT_CODES = {
    "Initial Exam":          ("99203", 150.00, 200.00),
    "Adjustment":            ("98940", 60.00,  90.00),
    "Therapeutic Exercise":  ("97110", 75.00,  100.00),
    "Massage Therapy":       ("97124", 65.00,  85.00),
    "X-Ray":                 ("72100", 120.00, 180.00),
    "Re-Examination":        ("99213", 100.00, 140.00),
}
INSURANCE_PAY_RATE = {
    "Medicare":     0.70,
    "Medicaid":     0.55,
    "Blue Cross":   0.80,
    "Aetna":        0.78,
    "UnitedHealth": 0.76,
    "Self-Pay":     0.45,
}

# ── HELPERS ──────────────────────────────────────────────────────────────────
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# ── GENERATORS ───────────────────────────────────────────────────────────────
def generate_providers(n=NUM_PROVIDERS):
    logger.info(f"Generating {n} providers...")
    providers = []
    for i in range(1, n + 1):
        providers.append({
            "provider_id": i,
            "name":        fake.name(),
            "specialty":   random.choice(["Chiropractor", "Chiropractic Assistant"]),
            "hire_date":   random_date(datetime(2015, 1, 1), datetime(2021, 12, 31)).date(),
        })
    return pd.DataFrame(providers)


def generate_patients(n=NUM_PATIENTS):
    logger.info(f"Generating {n} patients...")
    patients = []
    for i in range(1, n + 1):
        patients.append({
            "patient_id":     i,
            "first_name":    fake.first_name(),
            "last_name":     fake.last_name(),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=85).strftime("%Y-%m-%d"),
            "city":          fake.city(),
            "state":         fake.state_abbr(),
            "gender":         random.choice(["M", "F"]),
            "zip_code":       fake.zipcode(),
            "insurance_type": random.choice(INSURANCE_TYPES),
            "created_at":     random_date(START_DATE, END_DATE).date(),
        })
    return pd.DataFrame(patients)


def generate_appointments(patients_df, providers_df, n=NUM_APPTS):
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
    return pd.DataFrame(appts)


def generate_billing(appts_df, patients_df):
    logger.info("Generating billing records for completed appointments...")
    completed = appts_df[appts_df["status"] == "completed"].copy()
    billing   = []

    for _, appt in completed.iterrows():
        patient       = patients_df[patients_df["patient_id"] == appt["patient_id"]].iloc[0]
        cpt, low, high = CPT_CODES[appt["service_type"]]
        charge        = round(random.uniform(low, high), 2)
        pay_rate      = INSURANCE_PAY_RATE[patient["insurance_type"]]
        paid          = round(charge * pay_rate, 2)
        payment_date  = appt["appt_date"] + timedelta(days=random.randint(7, 45))

        billing.append({
            "billing_id":     len(billing) + 1,
            "appt_id":        appt["appt_id"],
            "patient_id":     appt["patient_id"],
            "cpt_code":       cpt,
            "service_type":   appt["service_type"],
            "charge_amount":  charge,
            "paid_amount":    paid,
            "insurance_type": patient["insurance_type"],
            "payment_date":   payment_date,
        })
    return pd.DataFrame(billing)


# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting synthetic data generation...")

    providers_df    = generate_providers()
    patients_df     = generate_patients()
    appointments_df = generate_appointments(patients_df, providers_df)
    billing_df      = generate_billing(appointments_df, patients_df)

    providers_df.to_csv("data/providers.csv",        index=False)
    patients_df.to_csv("data/patients.csv",           index=False)
    appointments_df.to_csv("data/appointments.csv",   index=False)
    billing_df.to_csv("data/billing.csv",             index=False)

    logger.info("✅ Data generation complete.")
    logger.info(f"   Providers:    {len(providers_df)}")
    logger.info(f"   Patients:     {len(patients_df)}")
    logger.info(f"   Appointments: {len(appointments_df)}")
    logger.info(f"   Billing rows: {len(billing_df)}")