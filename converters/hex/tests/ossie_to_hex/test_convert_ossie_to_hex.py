# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from pathlib import Path

from inline_snapshot import snapshot

from ossie_hex.ossie_to_hex.convert_ossie_to_hex import convert_ossie_to_hex
from tests.utils import hex_project_snapshot, problems_snapshot

TPCDS = Path(__file__).resolve().parents[4] / "examples" / "tpcds_semantic_model.yaml"


def test_convert_tpcds() -> None:
    hex_project, problems = convert_ossie_to_hex(
        TPCDS,
        None,
        dialect=None,
        hex_project_name=None,
    )
    assert hex_project_snapshot(hex_project) == snapshot("""\
name: tpcds_semantic_model
dialect: duckdb
resources:
- id: store_sales
  base_sql_table: tpcds.public.store_sales
  dimensions:
  - id: ss_sold_date_sk
    type: number
    expr_sql: ss_sold_date_sk
    description: Foreign key to date dimension
  - id: ss_item_sk
    type: number
    expr_sql: ss_item_sk
    description: Foreign key to item dimension
  - id: ss_customer_sk
    type: number
    expr_sql: ss_customer_sk
    description: Foreign key to customer dimension
  - id: ss_store_sk
    type: number
    expr_sql: ss_store_sk
    description: Foreign key to store dimension
  - id: ss_quantity
    type: number
    expr_sql: ss_quantity
    description: Quantity of items sold
  - id: ss_sales_price
    type: number
    expr_sql: ss_sales_price
    description: Sales price per unit
  - id: ss_ext_sales_price
    type: number
    expr_sql: ss_ext_sales_price
    description: Extended sales price (quantity * price)
  - id: ss_net_profit
    type: number
    expr_sql: ss_net_profit
    description: Net profit from the sale
  description: Fact table containing all store sales transactions
- id: date_dim
  base_sql_table: tpcds.public.date_dim
  dimensions:
  - id: d_date_sk
    type: number
    expr_sql: d_date_sk
    unique: true
    description: Surrogate key for date
  - id: d_date
    type: date
    expr_sql: d_date
    description: Actual date value
  - id: d_year
    type: number
    expr_sql: d_year
    description: Year
  - id: d_quarter_name
    type: string
    expr_sql: d_quarter_name
    description: Quarter name (e.g., 2024Q1)
  - id: d_month_name
    type: string
    expr_sql: d_month_name
    description: Month name
  description: Date dimension with calendar attributes
- id: customer
  base_sql_table: tpcds.public.customer
  dimensions:
  - id: c_customer_sk
    type: number
    expr_sql: c_customer_sk
    unique: true
    description: Surrogate key for customer
  - id: c_customer_id
    type: string
    expr_sql: c_customer_id
    description: Business key for customer
  - id: c_first_name
    type: string
    expr_sql: c_first_name
    description: Customer first name
  - id: c_last_name
    type: string
    expr_sql: c_last_name
    description: Customer last name
  - id: customer_full_name
    type: string
    expr_sql: c_first_name || ' ' || c_last_name
    description: Customer full name (computed field)
  - id: c_email_address
    type: string
    expr_sql: c_email_address
    description: Customer email address
  description: Customer dimension with demographic information
- id: item
  base_sql_table: tpcds.public.item
  dimensions:
  - id: i_item_sk
    type: number
    expr_sql: i_item_sk
    unique: true
    description: Surrogate key for item
  - id: i_item_id
    type: string
    expr_sql: i_item_id
    description: Business key for item
  - id: i_item_desc
    type: string
    expr_sql: i_item_desc
    description: Item description
  - id: i_brand
    type: string
    expr_sql: i_brand
    description: Brand name
  - id: i_category
    type: string
    expr_sql: i_category
    description: Item category
  - id: i_current_price
    type: number
    expr_sql: i_current_price
    description: Current price of the item
  description: Item/Product dimension with product attributes
- id: store
  base_sql_table: tpcds.public.store
  dimensions:
  - id: s_store_sk
    type: number
    expr_sql: s_store_sk
    unique: true
    description: Surrogate key for store
  - id: s_store_id
    type: string
    expr_sql: s_store_id
    unique: true
    description: Business key for store
  - id: s_store_name
    type: string
    expr_sql: s_store_name
    description: Store name
  - id: s_city
    type: string
    expr_sql: s_city
    description: City where store is located
  - id: s_state
    type: string
    expr_sql: s_state
    description: State where store is located
  - id: s_number_employees
    type: number
    expr_sql: s_number_employees
    description: Number of employees at the store
  description: Store dimension with location and store attributes
""")
    assert problems_snapshot(problems, include_causes=True) == snapshot("""\
[WARNING] Missing. Hex requires a datatype. Using default 'String'.
Cause: ['load', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_quarter_name', 'datatype']

[WARNING] Missing. Hex requires a datatype. Using default 'String'.
Cause: ['load', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_month_name', 'datatype']

[INFO] No Ossie dialect specified; using ANSI_SQL
Cause: ['load']

[WARNING] Composite primary key is not supported: ['ss_item_sk', 'ss_ticket_number']
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'primary_key']

[WARNING] Composite unique key is not supported: ['ss_item_sk', 'ss_ticket_number']
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'unique_keys']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_sold_date_sk', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_item_sk', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_customer_sk', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_store_sk', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_quantity', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_sales_price', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_ext_sales_price', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'fields', 'ss_net_profit', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store_sales', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_date', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_year', 'dimension']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_year', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_quarter_name', 'dimension']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_quarter_name', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_month_name', 'dimension']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'fields', 'd_month_name', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'date_dim', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'customer', 'fields', 'c_customer_id', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'customer', 'fields', 'customer_full_name', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'customer', 'fields', 'c_email_address', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'customer', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'item', 'fields', 'i_item_id', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'item', 'fields', 'i_item_desc', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'item', 'fields', 'i_brand', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'item', 'fields', 'i_category', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'item', 'fields', 'i_current_price', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'item', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store', 'fields', 's_store_id', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store', 'fields', 's_store_name', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store', 'fields', 's_city', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store', 'fields', 's_state', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store', 'fields', 's_number_employees', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'datasets', 'store', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'metrics', 'total_sales', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'metrics', 'total_profit', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'metrics', 'customer_lifetime_value', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'metrics', 'sales_by_brand', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'metrics', 'store_productivity', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'relationships', 'store_sales_to_date', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'relationships', 'store_sales_to_customer', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'relationships', 'store_sales_to_item', 'ai_context']

[WARNING] Not supported
Cause: ['convert', 'semantic_model', 'tpcds_retail_model', 'relationships', 'store_sales_to_store', 'ai_context']\
""")
