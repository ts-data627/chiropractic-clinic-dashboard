-- 5. Average appointments per patient
-- Business question: How often do patients return?

SELECT COUNT(appt_id)/COUNT(DISTINCT patient_id) as avg_appts
FROM appointments
WHERE status = 'Completed';
