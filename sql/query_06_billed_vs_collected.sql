-- 6. Billed vs collected by month
-- Business question: What is our collection rate trending over time?

SELECT 
	   DATE_TRUNC('month', payment_date::date) AS month,
	   ROUND(SUM(charge_amount::NUMERIC), 2) AS charge_amount,
	   ROUND(SUM(paid_amount::NUMERIC),2) AS paid_amount,
	   ROUND(SUM(paid_amount::NUMERIC) / SUM(charge_amount::NUMERIC) * 100, 2) AS total_reimbursement_rate
FROM billing
GROUP BY month
ORDER BY month;