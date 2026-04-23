-- One row per (system_id, metric_id): the most recent observation.
-- Prefers higher review_state ordering, then most recent observed_at.
CREATE OR REPLACE VIEW v_latest_observations AS
SELECT *
FROM observations
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY system_id, metric_id
    ORDER BY
        CASE review_state
            WHEN 'validated' THEN 3
            WHEN 'proposed' THEN 2
            WHEN 'superseded' THEN 1
            ELSE 0
        END DESC,
        observed_at DESC NULLS LAST
) = 1;
