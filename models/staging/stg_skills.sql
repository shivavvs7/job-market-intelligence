with source as (
    select * from {{ source('raw_market', 'skills') }}
),
flattened as (
    select
        skill_abr,
        skill_name
    from source
)
select * from flattened
