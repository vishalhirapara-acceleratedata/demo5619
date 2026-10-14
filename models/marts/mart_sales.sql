{{
    config(
        materialized='table',
        contract={'enforced': true}
    )
}}

with line_items as (

    select * from {{ ref('stg_orders') }}

),

-- One row per order: aggregate all line items into order-level totals.
-- Grain: one row per order_id.
final as (

    select
        cast(order_id                                                as varchar)      as order_id,
        cast(min(order_date)                                         as date)         as order_date,
        cast(min(customer_id)                                        as varchar)      as customer_id,
        cast(min(customer_name)                                      as varchar)      as customer_name,
        cast(sum(quantity)                                           as integer)      as total_items,
        cast(sum(coalesce(quantity, 0) * coalesce(unit_price, 0.00)) as decimal(10,2)) as total_revenue,
        cast(min(order_status)                                       as varchar)      as order_status

    from line_items
    group by order_id

)

select * from final
