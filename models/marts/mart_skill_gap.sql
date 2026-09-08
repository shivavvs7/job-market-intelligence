-- THE deliverable: compares OPUS candidates' real skills against actual
-- market demand extracted from 123,849 real job postings.
--
-- gap_status categorizes each skill:
--   'high_demand_low_coverage' - market wants it, few/no candidates have it
--     (the actionable recruiting signal)
--   'well_covered'             - candidate coverage is proportionate to demand
--   'niche_or_low_demand'      - candidates have it, market barely asks for it

with market as (
    select * from {{ ref('mart_skill_market_demand') }}
),

candidates as (
    select * from {{ ref('opus_candidate_skills') }}
)

select
    market.skill_normalized,
    market.postings_mentioning       as market_demand_count,
    market.pct_of_all_postings       as market_demand_pct,
    market.avg_max_salary_when_mentioned,
    coalesce(candidates.candidate_count, 0) as opus_candidate_count,
    case
        when market.pct_of_all_postings >= 5 and coalesce(candidates.candidate_count, 0) = 0
            then 'high_demand_low_coverage'
        when market.pct_of_all_postings >= 5 and coalesce(candidates.candidate_count, 0) > 0
            then 'well_covered'
        else 'niche_or_low_demand'
    end as gap_status
from market
left join candidates
    on market.skill_normalized = candidates.skill_normalized
order by market.postings_mentioning desc