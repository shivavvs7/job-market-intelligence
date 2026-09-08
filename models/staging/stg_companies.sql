with source as (
    select * from {{ source('raw_market', 'companies') }}
),
flattened as (
    select
        cast(company_id as string) as company_id,
        name                       as company_name,
        description                as company_description,
        company_size,
        state,
        country,
        city,
        zip_code,
        address,
        url                        as company_url
    from source
)
select * from flattened
