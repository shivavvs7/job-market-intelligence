-- Bridge table: many-to-many between jobs and skill categories.
-- One job can require multiple broad skill categories.

select
    js.job_id,
    js.skill_abr,
    sk.skill_name
from {{ ref('stg_job_skills') }} js
left join {{ ref('stg_skills') }} sk
    on js.skill_abr = sk.skill_abr
