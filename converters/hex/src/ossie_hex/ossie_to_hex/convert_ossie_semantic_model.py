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

from ossie import OSIDialect, OSIMetric, OSIRelationship, OSISemanticModel

from ..hex_extension import HexMeasureStash, HexProjectStash, read_stash
from ..hex_types import HexModel, HexResource
from ..util.errors import ConversionError
from ..util.pick_expression import pick_expression
from .context import ConvertOssieCtx
from .convert_ossie_dataset import convert_ossie_dataset
from .hex_ids import dataset_hex_ids, dimension_hex_ids
from .references import references
from .relationship_sides import relationship_sides
from .restore_hex_views import restore_hex_views


def convert_ossie_semantic_model(
    ossie_semantic_model: OSISemanticModel,
    ossie_dialect: OSIDialect,
    *,
    base_model: str | None = None,
    ctx: ConvertOssieCtx,
) -> list[HexResource]:
    """Convert Ossie semantic model to a Hex project

    Returns the converted Hex resources.
    """

    # Ossie names are free-form while Hex refs address Hex IDs, so resolve every
    # dataset up front and route relationship, metric, and expression qualifiers
    # through this map.
    taken_hex_resource_ids: set[str] = set()
    hex_ids_by_dataset = dataset_hex_ids(
        ossie_semantic_model, taken=taken_hex_resource_ids
    )
    # Relationship columns name fields on both sides, so every dataset's field
    # IDs must be resolvable before any single dataset is converted.
    dim_ids_by_dataset = {
        ds.name: dimension_hex_ids(ds) for ds in ossie_semantic_model.datasets
    }

    base_model_id = (
        hex_ids_by_dataset.get(base_model, base_model) if base_model else None
    )
    # Checked before use rather than where metrics are attached: an unknown name
    # would otherwise key `metrics_by_dataset` to a model no dataset reads back,
    # silently dropping every metric that fell through to it.
    if base_model_id is not None and base_model_id not in set(
        hex_ids_by_dataset.values()
    ):
        raise ConversionError(
            f"--base-model '{base_model}' does not name a dataset in "
            f"semantic model '{ossie_semantic_model.name}'"
        )

    # Index relationships by the Hex base (source) model.
    relations_by_dataset: dict[str, list[OSIRelationship]] = {}
    for rel in ossie_semantic_model.relationships or []:
        local = relationship_sides(rel).local_dataset
        base = hex_ids_by_dataset.get(local, local)
        relations_by_dataset.setdefault(base, []).append(rel)

    metrics_by_dataset = _assign_ossie_metrics(
        ossie_semantic_model,
        hex_ids_by_dataset=hex_ids_by_dataset,
        base_model_id=base_model_id,
        preferred_dialect=ossie_dialect,
    )

    hex_models: list[HexModel] = []
    for dataset in ossie_semantic_model.datasets:
        hex_id = hex_ids_by_dataset[dataset.name]
        hex_model = convert_ossie_dataset(
            dataset,
            hex_id=hex_id,
            hex_ids_by_dataset=hex_ids_by_dataset,
            dim_ids_by_dataset=dim_ids_by_dataset,
            preferred_dialect=ossie_dialect,
            relationships=relations_by_dataset.get(hex_id, []),
            metrics=metrics_by_dataset.get(hex_id, []),
            ctx=ctx,
        )
        hex_models.append(hex_model)

    hex_project_stash = read_stash(
        ossie_semantic_model.custom_extensions, HexProjectStash
    )
    hex_views = restore_hex_views(hex_project_stash, taken_ids=taken_hex_resource_ids)
    hex_resources = hex_models + hex_views
    return hex_resources


def _assign_ossie_metrics(
    model: OSISemanticModel,
    *,
    hex_ids_by_dataset: dict[str, str],
    base_model_id: str | None,
    preferred_dialect: OSIDialect,
) -> dict[str, list[OSIMetric]]:
    """Group a semantic model's metrics by the Hex model each belongs to.

    Ossie metrics sit beside the datasets rather than on one, while a Hex
    measure always belongs to a model, so every metric has to be placed before
    it can be converted.

    A metric goes where its custom extension says, else to the single dataset
    its expression names, else to ``base_model_id``. A metric that names several
    datasets with no base model to fall back on is an error rather than a guess.
    """
    ossie_dataset_names = set(hex_ids_by_dataset)
    hex_model_ids = set(hex_ids_by_dataset.values())

    metrics_by_dataset: dict[str, list[OSIMetric]] = {}
    unassigned: list[OSIMetric] = []
    for metric in model.metrics or []:
        stash = read_stash(metric.custom_extensions, HexMeasureStash)
        ds_id = stash.model_id if stash is not None else None
        if ds_id and ds_id in hex_model_ids:
            metrics_by_dataset.setdefault(ds_id, []).append(metric)
            continue
        refs = _datasets_referenced(metric, preferred_dialect, ossie_dataset_names)
        if len(refs) == 1:
            metrics_by_dataset.setdefault(hex_ids_by_dataset[refs[0]], []).append(
                metric
            )
        elif len(refs) == 0 and base_model_id:
            metrics_by_dataset.setdefault(base_model_id, []).append(metric)
        elif len(refs) == 0 and len(hex_model_ids) == 1:
            metrics_by_dataset.setdefault(next(iter(hex_model_ids)), []).append(metric)
        else:
            unassigned.append(metric)

    if unassigned:
        if base_model_id:
            for metric in unassigned:
                metrics_by_dataset.setdefault(base_model_id, []).append(metric)
        else:
            names = ", ".join(m.name for m in unassigned)
            raise ConversionError(
                f"Could not assign metric(s) to a Hex model: {names}. "
                f"Pass --base-model to choose a dataset."
            )

    return metrics_by_dataset


def _datasets_referenced(
    metric: OSIMetric,
    preferred_dialect: OSIDialect,
    dataset_names: set[str],
) -> list[str]:
    """Names from ``dataset_names`` that the metric's expression qualifies."""
    expr = pick_expression(metric.expression, preferred=preferred_dialect)
    if not expr:
        return []
    return [name for name in dataset_names if references(expr, name)]
