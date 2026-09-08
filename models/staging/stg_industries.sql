with source as (
    select * from {{ source('raw_market', 'industries') }}
),
flattened as (
    select
        cast(industry_id as string) as industry_id,
        industry_name
    from source
)
select * from flattened
