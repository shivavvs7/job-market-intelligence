with source as (
    select * from {{ source('raw_market', 'benefits') }}
),
flattened as (
    select
        cast(job_id as string) as job_id,
        type as benefit_type
    from source
)
select * from flattened
