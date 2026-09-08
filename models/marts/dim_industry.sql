select
    industry_id,
    industry_name
from {{ ref('stg_industries') }}
