with source as (
    select * from {{ source('raw_market', 'company_industries') }}
),
flattened as (
    select
        cast(company_id as string) as company_id,
        industry
    from source
)
select * from flattened
