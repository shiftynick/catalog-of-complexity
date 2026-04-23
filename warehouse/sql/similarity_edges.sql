-- Placeholder view. The analyze-archetypes skill will populate the `edges`
-- table with similarity edges derived from the system x metric matrix once
-- the registry has enough breadth. For now this view is a pass-through.
CREATE OR REPLACE VIEW v_similarity_edges AS
SELECT * FROM edges;
