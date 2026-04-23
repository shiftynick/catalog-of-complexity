-- Long-format system x metric matrix. Null value columns mean no observation
-- yet for that pair. Use this as the base for similarity / clustering work.
CREATE OR REPLACE VIEW v_system_metric_matrix AS
SELECT
    s.id                AS system_id,
    s.name              AS system_name,
    s.status            AS system_status,
    m.id                AS metric_id,
    m.name              AS metric_name,
    m.family            AS metric_family,
    o.value_numeric,
    o.value_text,
    o.value_boolean,
    o.unit,
    o.value_kind,
    o.confidence,
    o.review_state,
    o.observed_at
FROM systems s
CROSS JOIN metrics m
LEFT JOIN v_latest_observations o
       ON o.system_id = s.id
      AND o.metric_id = m.id;
