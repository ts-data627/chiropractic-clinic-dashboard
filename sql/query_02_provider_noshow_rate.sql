-- 2. No-show rate by provider
-- Business question: Which providers have the highest no-show rates?

SELECT
    p.provider_id,
    p.name,
    COUNT(*) FILTER (WHERE a.status = 'No-Show') AS no_show_count,
    COUNT(*) AS total_appointments,
    ROUND(
        COUNT(*) FILTER (WHERE a.status = 'No-Show') * 100.0 / COUNT(*),
        2
    ) AS no_show_rate_pct
FROM providers p
JOIN appointments a ON a.provider_id = p.provider_id
GROUP BY p.provider_id, p.name
ORDER BY no_show_rate_pct DESC;