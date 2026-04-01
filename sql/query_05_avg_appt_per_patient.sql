-- Query: Average appointments per patient
-- Business question: How often do patients return?
-- Table: healthcare_records
-- Author: Tevin S.
-- Date: 2026-03

SELECT COUNT(appt_id)/COUNT(DISTINCT patient_id) as avg_appts
FROM appointments
WHERE status = 'Completed';
