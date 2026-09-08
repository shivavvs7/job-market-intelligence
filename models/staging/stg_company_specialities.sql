with source as (
    select * from {{ source('raw_market', 'company_specialities') }}
),
flattened as (
    select
        cast(company_id as string) as company_id,
        speciality
    from source
)
select * from flattened
