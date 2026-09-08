with source as (
    select * from {{ source('raw_market', 'job_industries') }}
),
flattened as (
    select
        cast(job_id as string) as job_id,
        cast(industry_id as string) as industry_id
    from source
)
select * from flattened
