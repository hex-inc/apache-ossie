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

from __future__ import annotations

from ossie import OSIDataset, OSIField, OSIMetric, OSIRelationship

from ..hex_extension import HexModelStash, maybe_write_extension
from ..hex_types import HexDimension, HexMeasure, HexModel, HexRelation
from .context import ConvertHexCtx
from .convert_hex_dimension import convert_hex_dimension
from .convert_hex_measure import convert_hex_measure
from .convert_hex_relation import convert_hex_relation


def convert_hex_model(
    model: HexModel,
    *,
    metric_names: set[str],
    ctx: ConvertHexCtx,
) -> tuple[OSIDataset, list[OSIMetric], list[OSIRelationship]]:
    """Convert a Hex model to an Ossie dataset and the document-level entries it adds."""
    # Relations are converted first because whether a dimension's reference to
    # another model survives the trip back depends on which of them become
    # relationships.
    (
        relationships,
        unsupported_relations,
    ) = convert_hex_model_relations(model, ctx=ctx)

    (
        fields,
        unsupported_dimensions,
        primary_key,
        unique_keys,
    ) = convert_hex_model_dimensions(
        model,
        ctx=ctx,
    )

    metrics, unsupported_measures = convert_hex_model_measures(
        model,
        metric_names=metric_names,
        ctx=ctx,
    )

    # even though our parsing does well, it's better to be safe and preserve
    source_kind = "table" if model.base_sql_table else "query"

    stash = HexModelStash(
        display_name=model.name,
        source_kind=source_kind,
        visibility=model.visibility,
        dimensions=unsupported_dimensions or None,
        measures=unsupported_measures or None,
        relations=unsupported_relations or None,
    )

    dataset = OSIDataset(
        name=model.id,
        source=model.base_sql_table or model.base_sql_query or "",
        primary_key=primary_key,
        unique_keys=unique_keys,
        description=model.description or None,
        fields=fields or None,
        custom_extensions=maybe_write_extension(stash),
    )

    return dataset, metrics, relationships


def convert_hex_model_relations(
    model: HexModel,
    *,
    ctx: ConvertHexCtx,
) -> tuple[list[OSIRelationship], list[HexRelation]]:
    """Convert a model's relations, preserving ones Ossie cannot express."""
    relationships: list[OSIRelationship] = []
    unsupported_relations: list[HexRelation] = []
    for relation in model.relations:
        relationship, unsupported_relation = convert_hex_relation(
            relation,
            base_model_id=model.id,
            ctx=ctx,
        )
        if relationship is not None:
            relationships.append(relationship)
        elif unsupported_relation is not None:
            unsupported_relations.append(unsupported_relation)
    return relationships, unsupported_relations


def convert_hex_model_dimensions(
    model: HexModel,
    *,
    ctx: ConvertHexCtx,
) -> tuple[
    list[OSIField],
    list[HexDimension],
    list[str] | None,
    list[list[str]] | None,
]:
    """Convert a model's dimensions, collecting the ones marked unique.

    Returns a tuple of:
    - ``fields``: Ossie fields.
    - ``unsupported_dimensions``: dimensions Ossie cannot express.
    - ``primary_key``: Ossie primary key, if any.
    - ``unique_keys``: Ossie unique keys, if any.
    """
    fields: list[OSIField] = []
    unsupported_dimensions: list[HexDimension] = []
    unique_field_names: list[str] = []

    for dim in model.dimensions:
        field, unsupported_dimension = convert_hex_dimension(
            dim,
            model_id=model.id,
            ctx=ctx,
        )
        if field is not None:
            fields.append(field)
            if dim.unique:
                unique_field_names.append(dim.id)
        elif unsupported_dimension is not None:
            unsupported_dimensions.append(unsupported_dimension)

    primary_key: list[str] | None = None
    unique_keys: list[list[str]] | None = None
    if unique_field_names:
        # Hex doesn't have a concept of a primary key, so just use the first
        # unique field.
        primary_key = [unique_field_names[0]]
        # Hex marks each dimension unique on its own, and does not reflect composite keys
        unique_keys = [[name] for name in unique_field_names[1:]] or None

    return fields, unsupported_dimensions, primary_key, unique_keys


def convert_hex_model_measures(
    model: HexModel,
    *,
    metric_names: set[str],
    ctx: ConvertHexCtx,
) -> tuple[list[OSIMetric], list[HexMeasure]]:
    """Convert a model's measures, setting aside the ones Ossie cannot express."""
    metrics: list[OSIMetric] = []
    unsupported_measures: list[HexMeasure] = []
    for measure in model.measures:
        metric, unsupported_measure = convert_hex_measure(
            measure,
            model_id=model.id,
            metric_names=metric_names,
            ctx=ctx,
        )
        if metric is not None:
            metrics.append(metric)
        elif unsupported_measure is not None:
            unsupported_measures.append(unsupported_measure)
    return metrics, unsupported_measures
