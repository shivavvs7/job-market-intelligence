-- Confirmed in Stage 0: this dataset only has 35 BROAD skill categories
-- (e.g. "Information Technology", "Sales"), not granular skills like
-- "Python" or "Docker". This dimension reflects that honestly rather
-- than pretending it's more granular than it is.

select
    skill_abr,
    skill_name
from {{ ref('stg_skills') }}
