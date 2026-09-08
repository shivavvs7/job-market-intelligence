-- Cross-source text mining: for each job posting, flags which skills are
-- mentioned anywhere in the posting's description.
--
-- Skill vocabulary is a UNION of two independent sources:
--   1. opus_candidate_skills - the 31 REAL skills from OPUS candidates
--   2. general_tech_skills   - 25 common tech/business skills NOT already
--      covered by #1, added specifically so the gap analysis can detect
--      skills the market wants that NO OPUS candidate currently has.
--      Without this second list, every skill in the vocabulary would
--      already have at least 1 candidate by construction (it came FROM
--      a candidate), making the "high_demand_low_coverage" gap category
--      structurally impossible to ever trigger -- confirmed by running
--      the analysis once without this fix and seeing exactly that.
--
-- Design note: uses LOWER() + STRPOS for substring matching. An earlier
-- version tried CONTAINS_SUBSTR, but BigQuery requires that function's
-- search argument to be a compile-time constant -- it can't take a
-- column value that varies per row, which is exactly what's needed here.
-- STRPOS has no such restriction and gives the same case-insensitive
-- substring result once both sides are lowercased explicitly.
--
-- Known limitation, stated honestly: a short skill name could
-- theoretically match inside an unrelated longer word. A tradeoff of
-- substring matching vs. a fully whitespace/word-boundary-aware match.

with postings as (
    select job_id, description
    from {{ ref('stg_postings') }}
    where description is not null
),

skill_vocab as (
    select skill_normalized from {{ ref('opus_candidate_skills') }}
    union distinct
    select skill_normalized from {{ ref('general_tech_skills') }}
)

select
    p.job_id,
    v.skill_normalized
from postings p
cross join skill_vocab v
where strpos(lower(p.description), lower(v.skill_normalized)) > 0