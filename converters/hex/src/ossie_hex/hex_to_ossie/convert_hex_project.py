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

from ossie import (
    OSIDataset,
    OSIDocument,
    OSIMetric,
    OSIRelationship,
    OSISemanticModel,
    OSIVendor,
)

from ..hex_extension import HexProjectStash, HexViewStash, write_stash
from ..hex_types import HexModel, HexProject, HexView
from ..ossie_types import OSSIE_VERSION
from ..util.errors import ConversionError, ConversionWarning
from .context import ConvertHexCtx
from .convert_hex_model import convert_hex_model
from .convert_hex_view import convert_hex_view


def convert_hex_project(
    hex_project: HexProject,
    *,
    ctx: ConvertHexCtx,
) -> tuple[OSIDocument, list[ConversionWarning]]:
    """Convert a Hex project to an Ossie document.

    Returns ``(ossie_document, warnings)``.
    """
    datasets: list[OSIDataset] = []
    relationships: list[OSIRelationship] = []
    metrics: list[OSIMetric] = []
    views_stash: list[HexViewStash] = []
    metric_names: set[str] = set()

    for resource in hex_project.resources:
        if isinstance(resource, HexView):
            view_stash = convert_hex_view(resource, ctx=ctx)
            views_stash.append(view_stash)
            continue

        assert isinstance(resource, HexModel)
        dataset, ds_metrics, ds_rels = convert_hex_model(
            resource,
            metric_names=metric_names,
            ctx=ctx,
        )
        datasets.append(dataset)
        metrics.extend(ds_metrics)
        relationships.extend(ds_rels)

    if not datasets:
        raise ConversionError("Hex project contains no convertible models")

    project_stash = HexProjectStash(views=views_stash or None)

    semantic_model = OSISemanticModel(
        name=hex_project.name,
        datasets=datasets,
        relationships=relationships or None,
        metrics=metrics or None,
        custom_extensions=[write_stash(project_stash)],
    )
    document = OSIDocument(
        version=OSSIE_VERSION,
        dialects=[ctx.ossie_dialect],
        vendors=[OSIVendor.HEX],
        semantic_model=[semantic_model],
    )
    return document, ctx.warnings
