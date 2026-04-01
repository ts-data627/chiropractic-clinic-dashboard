import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import plotly.express as px

# --- Environment and Database Connection ---
load_dotenv()

engine = create_engine(
    f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
    f"@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
)

# --- Data loaders ---
@st.cache_data
def load_patients():
    return pd.read_sql("SELECT * FROM patients", engine)

@st.cache_data
def load_providers():
    return pd.read_sql("SELECT * FROM providers", engine)

@st.cache_data
def load_appointments():
    return pd.read_sql("SELECT * FROM appointments", engine)

@st.cache_data
def load_billing():
    return pd.read_sql("SELECT * FROM billing", engine)

# --- Load data ---
patients_df = load_patients()
providers_df = load_providers()
appointments_df = load_appointments()
billing_df = load_billing()


# --- Dashboard ---
st.title("Chiropractic Clinic Dashboard")

# --- Age Distribution ---
st.subheader("Patient Age Distribution")

age_bins = [0, 18, 34, 54, 74, 120]
age_labels = ["Under 18", "18-34", "35-54", "55-74", "75+"]

patients_df["age_group"] = pd.cut(
    patients_df["age"],
    bins=age_bins,
    labels=age_labels
)

age_dist = patients_df["age_group"].value_counts().sort_index()

st.bar_chart(age_dist)

# --- Monthly New Patient Acquisition ---

patients_df["month"] = pd.to_datetime(patients_df["created_at"]).dt.to_period("M").astype(str)
monthly = patients_df.groupby("month").size().reset_index(name="new_patients")

fig = px.bar(
    monthly,
    x="month",
    y="new_patients",
    title="New Patient Acquisition by Month",
    labels={"month": "Month", "new_patients": "New Patients"}
)
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig)

# --- No-Show Rate by Provider ---

def no_show_rate_per_provider(appts_df: pd.DataFrame) -> pd.DataFrame:
    df = appts_df.copy()

    # Normalize just in case
    df['status'] = df['status'].str.lower()

    # Define valid appointments (exclude cancelled)
    df = df[df['status'].isin(['completed', 'no-show'])]

    # Create flag
    df['is_no_show'] = df['status'] == 'no-show'

    # Aggregate
    result = (
        df.groupby('provider_id')
        .agg(
            total_appointments=('appt_id', 'count'),
            no_show_count=('is_no_show', 'sum')
        )
        .reset_index()
    )

    # Rate
    result['no_show_rate'] = result['no_show_count'] / result['total_appointments']

    # Clean presentation
    result['no_show_rate_pct'] = (result['no_show_rate'] * 100).round(2)

    return result.sort_values(by='no_show_rate', ascending=False)

def no_show_with_provider_names(appts_df, providers_df):
    result = no_show_rate_per_provider(appts_df)

    result = result.merge(
        providers_df[['provider_id', 'name']],
        on='provider_id',
        how='left'
    )

    return result[['provider_id', 'name', 'total_appointments', 'no_show_count', 'no_show_rate_pct']]

appts_df = appointments_df
providers_df = providers_df

df = no_show_with_provider_names(appts_df, providers_df)

st.title("No-Show Rate per Provider")

# Table
st.dataframe(df, use_container_width=True)

# Chart (this is what actually matters)
chart_df = df.set_index('name')['no_show_rate_pct']

st.subheader("No-Show Rate (%)")
fig = px.bar(
    df,
    x="name",
    y="no_show_rate_pct",
    title="No-Show Rate by Provider",
    labels={"name": "Provider", "no_show_rate_pct": "No-Show Rate (%)"}
)
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig)