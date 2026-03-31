-- 1. Monthly appointment volume
-- Business question: How is appointment volume trending month over month?
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', appt_date) AS month,
        COUNT(*) AS appointment_count
    FROM appointments
    GROUP BY 1
),
with_lag AS (
    SELECT
        month,
        appointment_count,
        LAG(appointment_count) OVER (ORDER BY month) AS prev_month
    FROM monthly
)
SELECT
    month,
    appointment_count,
    prev_month,
    appointment_count - prev_month AS mom_change,
    ROUND(
        (appointment_count - prev_month) * 100.0 / NULLIF(prev_month, 0),
2
    ) AS mom_pct_change
FROM with_lag
ORDER BY month;