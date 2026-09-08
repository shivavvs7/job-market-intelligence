-- Market demand signal per skill: how many postings mention it, what
-- fraction of the total market that represents, and the average max
-- salary among postings that mention it (using fact_job_postings'
-- COALESCE'd salary field, which favors the more reliable salaries.csv
-- source per the Stage 0/2 finding).

with mentions as (
    select * from {{ ref('int_posting_skill_mentions') }}
),

postings_with_salary as (
    select job_id, max_salary
    from {{ ref('fact_job_postings') }}
),

total_postings as (
    select count(*) as total from {{ ref('fact_job_postings') }}
)

select
    m.skill_normalized,
    count(distinct m.job_id) as postings_mentioning,
    round(100 * count(distinct m.job_id) / (select total from total_postings), 2) as pct_of_all_postings,
    round(avg(p.max_salary), 0) as avg_max_salary_when_mentioned
from mentions m
left join postings_with_salary p
    on m.job_id = p.job_id
group by m.skill_normalized
order by postings_mentioning desc