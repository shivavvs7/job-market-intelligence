-- Feature table for the Stage 4 salary prediction model.
-- One row per posting with usable salary data, with the most in-demand
-- skills (from mart_skill_market_demand) pivoted into binary flag
-- columns -- a standard "wide" feature format for a regression model.
--
-- Filtered to salary_source = 'salaries_table' only (not the fallback
-- postings_table values) -- per the Stage 0/2 finding, this is the
-- more reliable source (16.8% null vs 71-95% null), so the training
-- target variable is built on the higher-quality data deliberately,
-- not just "whatever wasn't null".

with postings as (
    select *
    from {{ ref('fact_job_postings') }}
    where salary_source = 'salaries_table'
      and max_salary is not null
),

company as (
    select company_id, employee_count, primary_industry
    from {{ ref('dim_company') }}
),

skill_mentions as (
    select * from {{ ref('int_posting_skill_mentions') }}
)

select
    p.job_id,
    p.max_salary,
    p.experience_level,
    p.work_type,
    p.remote_allowed,
    -- crude state extraction: "Austin, TX" -> "TX". Nulls for
    -- country-only entries like "United States" -- a real, acknowledged
    -- limitation of this quick parsing approach.
    trim(split(p.location, ',')[safe_offset(1)]) as state,
    c.employee_count,
    c.primary_industry,

    max(case when sm.skill_normalized = 'python' then 1 else 0 end)            as has_python,
    max(case when sm.skill_normalized = 'sql' then 1 else 0 end)               as has_sql,
    max(case when sm.skill_normalized = 'aws' then 1 else 0 end)               as has_aws,
    max(case when sm.skill_normalized = 'cloud' then 1 else 0 end)             as has_cloud,
    max(case when sm.skill_normalized = 'java' then 1 else 0 end)              as has_java,
    max(case when sm.skill_normalized = 'excel' then 1 else 0 end)             as has_excel,
    max(case when sm.skill_normalized = 'docker' then 1 else 0 end)            as has_docker,
    max(case when sm.skill_normalized = 'kubernetes' then 1 else 0 end)        as has_kubernetes,
    max(case when sm.skill_normalized = 'azure' then 1 else 0 end)             as has_azure,
    max(case when sm.skill_normalized = 'react' then 1 else 0 end)             as has_react,
    max(case when sm.skill_normalized = 'javascript' then 1 else 0 end)        as has_javascript,
    max(case when sm.skill_normalized = 'agile' then 1 else 0 end)             as has_agile,
    max(case when sm.skill_normalized = 'spark' then 1 else 0 end)             as has_spark,
    max(case when sm.skill_normalized = 'machine learning' then 1 else 0 end)  as has_machine_learning,
    max(case when sm.skill_normalized = 'data engineering' then 1 else 0 end)  as has_data_engineering

from postings p
left join company c on p.company_id = c.company_id
left join skill_mentions sm on p.job_id = sm.job_id
group by
    p.job_id, p.max_salary, p.experience_level, p.work_type,
    p.remote_allowed, p.location, c.employee_count, c.primary_industry