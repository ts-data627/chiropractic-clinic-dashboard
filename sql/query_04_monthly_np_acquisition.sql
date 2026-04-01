-- Query: New patient acquisition by month
-- Business question: Are we growing our patient base over time?
-- Table: healthcare_records
-- Author: Tevin S.
-- Date: 2026-03

SELECT
    DATE_TRUNC('month', created_at::date) AS month,
    COUNT(*) AS new_patients
FROM patients
GROUP BY 1
ORDER BY month;
