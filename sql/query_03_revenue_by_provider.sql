-- Query: Revenue by provider
-- Business question: Which providers are driving the most revenue?
-- Table: healthcare_records
-- Author: Tevin S.
-- Date: 2026-03

SELECT a.provider_id, p.name, ROUND(SUM(b.paid_amount)::numeric, 2) AS revenue
FROM appointments a
JOIN billing b ON a.appt_id = b.appt_id
JOIN providers p ON a.provider_id = p.provider_id
GROUP BY a.provider_id, p.name
ORDER BY revenue DESC;
