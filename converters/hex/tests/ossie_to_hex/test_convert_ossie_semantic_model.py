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

import pytest
from inline_snapshot import snapshot
from ossie import (
    OSIDataset,
    OSIMetric,
    OSIRelationship,
    OSISemanticModel,
)

from ossie_hex.hex import HexModel, HexRelationType
from ossie_hex.ossie_to_hex.context import ExportContext
from ossie_hex.ossie_to_hex.convert_ossie_semantic_model import (
    convert_ossie_semantic_model,
)
from tests.ossie_to_hex.utils import Quick
from tests.utils import problems_snapshot


def _model_by_id(models: list[HexModel], id: str) -> HexModel | None:
    return next(model for model in models if model.id == id)


def _model_measure_ids(model: HexModel) -> list[str]:
    return [measure.id for measure in model.measures]


def _model_relation_ids(model: HexModel) -> list[str]:
    return [relation.id for relation in model.relations]


@pytest.fixture
def order_customer() -> OSIRelationship:
    return Quick.relationship(
        "order_customer", "orders", "customers", ["customer_id"], ["id"]
    )


@pytest.fixture
def sales_per_customer() -> OSIMetric:
    return Quick.metric(
        "sales_per_customer",
        "Decimal",
        [("ANSI_SQL", "SUM(orders.amount) / COUNT(DISTINCT customers.id)")],
    )


@pytest.fixture
def orders() -> OSIDataset:
    return Quick.dataset(
        "orders",
        "public.orders",
        [
            ("amount", "Integer", [("ANSI_SQL", "amount")]),
            ("customer_id", "String", [("ANSI_SQL", "customer_id")]),
        ],
    )


@pytest.fixture
def customers() -> OSIDataset:
    return Quick.dataset(
        "customers",
        "public.customers",
        [("id", "String", [("ANSI_SQL", "id")])],
    )


@pytest.fixture
def ctx() -> ExportContext:
    ctx = ExportContext()
    ctx._set_dialects("ANSI_SQL", "duckdb")
    return ctx


def test_assigns_metric_and_relationship(
    ctx: ExportContext,
    orders: OSIDataset,
    customers: OSIDataset,
    order_customer: OSIRelationship,
    sales_per_customer: OSIMetric,
) -> None:
    """Assigns a metric and relationship to the correct model.

    Does not
      - assign metric more than once
      - assign to a model not referenced by the metric
      - assign relationship more than once for a single metric
    """
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[orders, customers],
        relationships=[order_customer],
        metrics=[sales_per_customer],
    )
    result = convert_ossie_semantic_model(
        semantic_model,
        ctx=ctx,
    )

    assert len(result) == 2
    orders_model = _model_by_id(result, "orders")
    customers_model = _model_by_id(result, "customers")
    assert orders_model is not None
    assert customers_model is not None
    assert len(customers_model.measures) == 0
    assert len(orders_model.measures) == 1
    measure = orders_model.measures[0]
    assert measure.id == "sales_per_customer"
    assert measure.func_sql == snapshot(
        "SUM(${amount}) / COUNT(DISTINCT ${order_customer.id})"
    )

    assert len(customers_model.relations) == 0
    assert len(orders_model.relations) == 1
    relation = orders_model.relations[0]
    assert relation.id == "order_customer"
    assert relation.target == "customers"
    assert relation.type == HexRelationType.MANY_TO_ONE
    assert relation.join_sql == snapshot("customer_id = ${order_customer}.id")

    assert not ctx.problems


def test_assignment_prefers_from_to_direction(
    ctx: ExportContext,
    orders: OSIDataset,
    customers: OSIDataset,
    order_customer: OSIRelationship,
    sales_per_customer: OSIMetric,
) -> None:
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[customers, orders],  # different dataset order
        relationships=[order_customer],
        metrics=[sales_per_customer],
    )
    result = convert_ossie_semantic_model(
        semantic_model,
        ctx=ctx,
    )

    assert len(result) == 2
    customers_model = _model_by_id(result, "customers")
    orders_model = _model_by_id(result, "orders")
    assert customers_model is not None
    assert orders_model is not None
    assert _model_measure_ids(customers_model) == snapshot([])
    assert _model_measure_ids(orders_model) == snapshot(["sales_per_customer"])

    assert _model_relation_ids(customers_model) == snapshot([])
    assert _model_relation_ids(orders_model) == snapshot(["order_customer"])


def test_drops_metric_that_no_dataset_can_resolve(
    ctx: ExportContext,
    orders: OSIDataset,
    customers: OSIDataset,
    sales_per_customer: OSIMetric,
) -> None:
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[orders, customers],
        relationships=[],
        metrics=[sales_per_customer],
    )
    result = convert_ossie_semantic_model(semantic_model, ctx=ctx)

    assert all(model.measures == [] for model in result)
    assert problems_snapshot(ctx.problems) == snapshot(
        "[ERROR] Cannot assign metric. Unable to find a relationship between referenced datasets: orders, customers."
    )


def test_does_not_choose_between_parallel_relationships(
    ctx: ExportContext,
    orders: OSIDataset,
    customers: OSIDataset,
    sales_per_customer: OSIMetric,
) -> None:
    billing_customer = Quick.relationship(
        "billing_customer", "orders", "customers", ["billing_customer_id"], ["id"]
    )
    shipping_customer = Quick.relationship(
        "shipping_customer", "orders", "customers", ["shipping_customer_id"], ["id"]
    )
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[orders, customers],
        relationships=[billing_customer, shipping_customer],
        metrics=[sales_per_customer],
    )
    result = convert_ossie_semantic_model(semantic_model, ctx=ctx)

    assert len(result) == 2
    orders_model = _model_by_id(result, "orders")
    customers_model = _model_by_id(result, "customers")
    assert orders_model is not None
    assert customers_model is not None
    orders_relation_ids = _model_relation_ids(orders_model)
    customers_relation_ids = _model_relation_ids(customers_model)
    assert orders_relation_ids == snapshot(["billing_customer", "shipping_customer"])
    assert customers_relation_ids == snapshot([])

    assert problems_snapshot(ctx.problems) == snapshot(
        "[WARNING] Ambiguous metric assignment. Multiple relationships found between referenced datasets: orders, customers. Possible relationships: billing_customer, shipping_customer."
    )


def test_drops_metric_without_a_dataset_reference(
    ctx: ExportContext,
    orders: OSIDataset,
) -> None:
    row_count = Quick.metric("row_count", "Integer", [("ANSI_SQL", "COUNT(*)")])
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[orders],
        metrics=[row_count],
    )
    result = convert_ossie_semantic_model(semantic_model, ctx=ctx)

    assert result[0].measures == []
    assert problems_snapshot(ctx.problems) == snapshot(
        "[ERROR] Referencing no datasets is not supported."
    )


def test_reports_metric_with_more_than_two_dataset_references(
    ctx: ExportContext,
    orders: OSIDataset,
    customers: OSIDataset,
) -> None:
    stores = Quick.dataset(
        "stores",
        "public.stores",
        [("id", "String", [("ANSI_SQL", "id")])],
    )
    metric = Quick.metric(
        "three_dataset_metric",
        "Integer",
        [("ANSI_SQL", "orders.amount + customers.id + stores.id")],
    )
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[orders, customers, stores],
        metrics=[metric],
    )

    result = convert_ossie_semantic_model(semantic_model, ctx=ctx)

    assert all(model.measures == [] for model in result)
    assert problems_snapshot(ctx.problems) == snapshot(
        "[ERROR] Referencing more than two datasets is not supported. Found 3: orders, customers, stores."
    )


def test_fully_processes_unassigned_metric(
    ctx: ExportContext,
    orders: OSIDataset,
) -> None:
    metric = Quick.metric("row_count", "Integer", [("ANSI_SQL", "COUNT(*)")])
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[orders],
        metrics=[metric],
    )

    result = convert_ossie_semantic_model(semantic_model, ctx=ctx)

    assert result[0].measures == []
    assert problems_snapshot(ctx.problems) == snapshot(
        "[ERROR] Referencing no datasets is not supported."
    )


def test_assigns_relationship_not_used_by_a_metric(
    ctx: ExportContext,
    orders: OSIDataset,
    customers: OSIDataset,
    order_customer: OSIRelationship,
) -> None:
    semantic_model = OSISemanticModel(
        name="sales",
        datasets=[orders, customers],
        relationships=[order_customer],
        metrics=[],
    )
    result = convert_ossie_semantic_model(semantic_model, ctx=ctx)

    assert [relation.id for relation in result[0].relations] == ["order_customer"]
    assert result[1].relations == []
    assert not ctx.problems
