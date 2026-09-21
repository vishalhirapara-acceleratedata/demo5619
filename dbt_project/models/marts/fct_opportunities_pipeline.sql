-- Sales pipeline dashboard fact table
-- One row per opportunity with account and owner context for the sales team
-- Supports deal tracking, pipeline health, and close probability analysis

with opportunities as (
    select
        id,
        account_id,
        name,
        amount,
        stage,
        close_date,
        probability,
        created_date,
        modified_date,
        owner_id
    from {{ source('salesforce', 'opportunities') }}
),

accounts as (
    select
        id,
        name as account_name,
        industry,
        annual_revenue
    from {{ source('salesforce', 'accounts') }}
),

users as (
    select
        id,
        first_name,
        last_name,
        email,
        username
    from {{ source('salesforce', 'users') }}
),

enriched as (
    select
        opp.id as opportunity_id,
        opp.name as opportunity_name,
        opp.amount,
        opp.stage,
        opp.probability,
        opp.close_date,
        acc.account_name,
        acc.industry,
        acc.annual_revenue,
        usr.first_name as owner_first_name,
        usr.last_name as owner_last_name,
        usr.email as owner_email,
        usr.username as owner_username,
        opp.created_date,
        opp.modified_date,
        cast(opp.modified_date as date) as last_modified_date,
        current_timestamp() as dbt_loaded_at
    from opportunities opp
    left join accounts acc on opp.account_id = acc.id
    left join users usr on opp.owner_id = usr.id
)

select * from enriched
