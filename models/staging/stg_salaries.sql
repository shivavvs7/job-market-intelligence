-- Staging for the DEDICATED salary table, confirmed in Stage 0 to have far
-- better coverage (16.8% null) than postings.csv's own salary columns
-- (71-95% null). This is the primary salary source for fact_job_postings.

with source as (
    select * from {{ source('raw_market', 'salaries') }}
),
flattened as (
    select
        job_id,
        safe_cast(max_salary as float64) as max_salary,
        safe_cast(min_salary as float64) as min_salary,
        safe_cast(med_salary as float64) as med_salary,
        pay_period,
        currency,
        compensation_type
    from source
)
select * from flattened