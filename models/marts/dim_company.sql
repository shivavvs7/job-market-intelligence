-- Company dimension: joins companies with their primary industry and
-- latest employee count snapshot. A company can have multiple
-- specialities/industries in the source tables (many-to-many) -- this
-- model picks one industry per company (first alphabetically) to keep
-- the dimension at one-row-per-company grain, appropriate for a
-- dimension table. Full industry detail remains queryable via
-- stg_company_industries directly if ever needed.

with companies as (
    select * from {{ ref('stg_companies') }}
),

primary_industry as (
    select
        company_id,
        industry,
        row_number() over (partition by company_id order by industry) as rn
    from {{ ref('stg_company_industries') }}
),

latest_employee_count as (
    select
        company_id,
        employee_count,
        follower_count,
        recorded_at,
        row_number() over (partition by company_id order by recorded_at desc) as rn
    from {{ ref('stg_employee_counts') }}
)

select
    c.company_id,
    c.company_name,
    c.city,
    c.state,
    c.country,
    c.company_size,
    pi.industry as primary_industry,
    lec.employee_count,
    lec.follower_count
from companies c
left join primary_industry pi
    on c.company_id = pi.company_id and pi.rn = 1
left join latest_employee_count lec
    on c.company_id = lec.company_id and lec.rn = 1
