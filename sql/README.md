# SQL Analytics Layer #

This folder contains analytical queries built against a synthetic chiropractic clinic dataset loaded into AWS RDS PostgreSQL. Each query answers a distinct and realistic business question about providers, patients, appointments, and billing.

## Queries ##

### 01 -- Monthly Appointment Volume ###

File: `query_01_monthly_appointment_volume.sql`
Tracks total appointment volume by month with month-over-month change and percent change. Shows the rate of change compared to previous month.

### 02 -- Provider No-Show Rate ###

File: `query_02_provider_noshow_rate.sql`
Shows the number of "No-Show" appointment statuses per each provider. Provides the rate of "No-Show" appointments ranked for each provider.

### 03 -- Revenue by Provider ###

File: `query_03_revenue_by_provider.sql`
Provides the total revenue collected for each provider. Ranks the total revenue highest to lowest.

### 04 -- Monthly New Patient Acquisitions ###

File: `query_04_monthly_np_acquisition.sql`
Shows the total number of new patients seen at the clinic per month.

### 05 -- Average Appointments per Patient ###

File: `query_05_avg_appt_per_patient.sql`
Shows the average number of visits to the office per patient. Only appointments marked "Completed" are used in this analysis.

### 06 -- Billed Amount vs. Collected Amounts ###

File: `query_06_billed_vs_collected.sql`
Shows the amounts billed vs. the amounts actually collected for each month. Breaks down the actual reimbursement rate by month.

### 07 -- Patient Age Distribution ###

File: `query_07_patient_age_distribution.sql`
Breaks down the patient population by age group to identify which demographics the clinic serves most.
