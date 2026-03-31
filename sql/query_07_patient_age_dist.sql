-- 7. Patient age distribution
-- Business question: What age groups make up our patient population?

SELECT 
	CASE
	    WHEN age < 18 THEN 'Under 18'
	    WHEN age BETWEEN 18 AND 34 THEN '18-34'
	    WHEN age BETWEEN 35 AND 54 THEN '35-54'
	    WHEN age BETWEEN 55 AND 74 THEN '55-74'
    ELSE '75+'
	END AS age_group,
	COUNT(*)
FROM patients
GROUP BY age_group
ORDER BY MIN(age);