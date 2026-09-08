-- Staging: job postings, the core fact source.
-- Raw layer stores everything as STRING (see ingestion script's design
-- note). Numeric fields are cast via SAFE_CAST through FLOAT64 first,
-- not straight to INT64 -- confirmed some integer-like fields (views,
-- applies) were exported as "1.0"-style strings (a classic pandas quirk:
-- a column with any nulls gets silently upgraded to float dtype, which
-- then affects how present values are written to CSV). A direct
-- CAST(STRING AS INT64) rejects a decimal-point string outright.
-- SAFE_CAST (rather than CAST) throughout so an unexpected value
-- produces NULL instead of failing the whole model build.
--
-- Note: max_salary/min_salary/med_salary/normalized_salary here are the
-- postings.csv's OWN salary fields, confirmed 71-95% null in Stage 0.
-- These are kept for reference but fact_job_postings uses salaries.csv
-- (via stg_salaries) as the primary salary source instead.

with source as (
    select * from {{ source('raw_market', 'postings') }}
),

flattened as (
    select
        job_id,
        company_id,
        company_name,
        title,
        description,
        location,
        formatted_work_type                                as work_type,
        formatted_experience_level                         as experience_level,
        safe_cast(remote_allowed as float64)                as remote_allowed,
        safe_cast(safe_cast(views as float64) as int64)     as views,
        safe_cast(safe_cast(applies as float64) as int64)   as applies,
        safe_cast(max_salary as float64)                    as posting_max_salary,
        safe_cast(min_salary as float64)                    as posting_min_salary,
        safe_cast(med_salary as float64)                    as posting_med_salary,
        safe_cast(normalized_salary as float64)             as posting_normalized_salary,
        pay_period,
        currency,
        compensation_type,
        timestamp_seconds(safe_cast(safe_cast(listed_time as float64) / 1000 as int64))          as listed_at,
        timestamp_seconds(safe_cast(safe_cast(original_listed_time as float64) / 1000 as int64)) as originally_listed_at,
        timestamp_seconds(safe_cast(safe_cast(expiry as float64) / 1000 as int64))                as expires_at
    from source
)

select * from flattened