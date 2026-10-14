with source as (

    select * from {{ ref('orders') }}

),

staged as (

    select
        cast(order_id      as varchar)       as order_id,
        cast(order_date    as date)          as order_date,
        cast(customer_id   as varchar)       as customer_id,
        cast(customer_name as varchar)       as customer_name,
        cast(product_id    as varchar)       as product_id,
        cast(product_name  as varchar)       as product_name,
        cast(category      as varchar)       as category,
        cast(quantity      as integer)       as quantity,
        cast(unit_price    as decimal(10,2)) as unit_price,
        cast(order_status  as varchar)       as order_status

    from source

)

select * from staged
