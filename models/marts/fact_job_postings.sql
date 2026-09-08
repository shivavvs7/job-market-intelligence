-- Core fact table: one row per job posting.
--
-- Salary handling (per the Stage 0 finding): salaries.csv has far better
-- coverage than postings.csv's own salary fields, so it's used as the
-- PRIMARY source via COALESCE, falling back to the posting's own fields
-- only when salaries.csv has no match. A flag column records which
-- source actually supplied the value, so downstream analysis (e.g. the
-- salary prediction model in Stage 4) can account for provenance rather
-- than treating all salary values as equally reliable.

with postings as (
    select * from {{ ref('stg_postings') }}
),

salaries as (
    select * from {{ ref('stg_salaries') }}
)

select
    p.job_id,
    p.company_id,
    p.company_name,
    p.title,
    p.location,
    p.work_type,
    p.experience_level,
    p.remote_allowed,
    p.views,
    p.applies,

    coalesce(s.max_salary, p.posting_max_salary)   as max_salary,
    coalesce(s.min_salary, p.posting_min_salary)   as min_salary,
    coalesce(s.med_salary, p.posting_med_salary)   as med_salary,
    coalesce(s.pay_period, p.pay_period)           as pay_period,
    coalesce(s.currency, p.currency)               as currency,
    case
        when s.job_id is not null then 'salaries_table'
        when p.posting_max_salary is not null then 'postings_table'
        else 'none'
    end as salary_source,

    p.listed_at,
    p.originally_listed_at,
    p.expires_at
from postings p
left join salaries s
    on p.job_id = s.job_id
