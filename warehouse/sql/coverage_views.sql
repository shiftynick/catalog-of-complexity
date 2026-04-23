-- Operational dashboard views: how much of the universe is populated and at
-- what quality. Use these for workflow-health tracking.
CREATE OR REPLACE VIEW v_coverage_summary AS
SELECT
    (SELECT COUNT(*) FROM systems)                                           AS systems_total,
    (SELECT COUNT(*) FROM metrics)                                           AS metrics_total,
    (SELECT COUNT(*) FROM sources)                                           AS sources_total,
    (SELECT COUNT(*) FROM observations)                                      AS observations_total,
    (SELECT COUNT(*) FROM observations WHERE review_state = 'validated')     AS observations_validated,
    (SELECT COUNT(*) FROM observations WHERE review_state = 'auto-validated') AS observations_auto_validated,
    (SELECT COUNT(*) FROM observations WHERE review_state = 'proposed')      AS observations_proposed,
    CASE
        WHEN (SELECT COUNT(*) FROM systems) = 0
          OR (SELECT COUNT(*) FROM metrics) = 0 THEN 0.0
        ELSE CAST(
                 (SELECT COUNT(*) FROM observations
                    WHERE review_state IN ('validated', 'auto-validated'))
                 AS DOUBLE
             )
             / ((SELECT COUNT(*) FROM systems) * (SELECT COUNT(*) FROM metrics))
    END                                                                      AS usable_coverage,
    CASE
        WHEN (SELECT COUNT(*) FROM systems) = 0
          OR (SELECT COUNT(*) FROM metrics) = 0 THEN 0.0
        ELSE CAST(
                 (SELECT COUNT(*) FROM observations WHERE review_state = 'validated')
                 AS DOUBLE
             )
             / ((SELECT COUNT(*) FROM systems) * (SELECT COUNT(*) FROM metrics))
    END                                                                      AS human_validated_coverage;

CREATE OR REPLACE VIEW v_coverage_by_family AS
SELECT
    m.family                                                                 AS metric_family,
    COUNT(DISTINCT m.id)                                                     AS metrics_in_family,
    COUNT(DISTINCT o.system_id)                                              AS systems_with_observation,
    COUNT(o.observation_id)                                                  AS observations_total,
    SUM(CASE WHEN o.review_state = 'validated' THEN 1 ELSE 0 END)            AS observations_validated,
    SUM(CASE WHEN o.review_state = 'auto-validated' THEN 1 ELSE 0 END)       AS observations_auto_validated
FROM metrics m
LEFT JOIN observations o ON o.metric_id = m.id
GROUP BY m.family
ORDER BY m.family;
