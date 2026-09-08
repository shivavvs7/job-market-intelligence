with source as (
    select * from {{ source('raw_market', 'employee_counts') }}
),
flattened as (
    select
        company_id,
        safe_cast(employee_count as int64) as employee_count,
        safe_cast(follower_count as int64) as follower_count,
        timestamp_seconds(safe_cast(time_recorded as int64)) as recorded_at
    from source
)
select * from flattened