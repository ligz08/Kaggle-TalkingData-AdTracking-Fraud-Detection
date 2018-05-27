DROP VIEW IF EXISTS {schema_name}.{out_table_name};
CREATE VIEW {schema_name}.{out_table_name} AS
SELECT
    {by_feature},
    COUNT(*) AS clicks_by_{by_feature},
    SUM(is_attributed) AS downloads_by_{by_feature},
    SUM(is_attributed)::FLOAT / COUNT(*) AS download_ratio_by_{by_feature} 
FROM
    {schema_name}.{in_table_name}
GROUP BY
    {by_feature}
;
