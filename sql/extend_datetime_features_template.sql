DROP VIEW IF EXISTS {schema_name}.{out_table_name};
CREATE OR REPLACE VIEW {schema_name}.{out_table_name} AS
SELECT
    *,
    DATE_PART('hour', click_time) AS click_hour,
    DATE_PART('minute', click_time) AS click_minute,
    DATE_PART('second', click_time) AS click_second,
    DATE_PART('minute', click_time)::INTEGER % 15 AS click_minute_mod15,
    DATE_PART('second', click_time)::INTEGER % 5 AS click_second_mod5
FROM
    {schema_name}.{in_table_name}
;
