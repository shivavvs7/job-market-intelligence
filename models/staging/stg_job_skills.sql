with source as (
    select * from {{ source('raw_market', 'job_skills') }}
),
flattened as (
    select
        cast(job_id as string) as job_id,
        skill_abr
    from source
)
select * from flattened
