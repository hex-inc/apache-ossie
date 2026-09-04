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
    OssieDataset,
    OssieDocument,
    OssieMetric,
    OssieRelationship,
    OssieSemanticModel,
)

from ..hex import HexProject
from .context import ImportContext
from .convert_hex_model import convert_hex_model
from .convert_hex_view import convert_hex_view


def convert_hex_project(
    hex_project: HexProject,
    *,
    ctx: ImportContext,
) -> OssieDocument:
    """Convert a Hex project to an Ossie document."""

    with ctx.problem_scope("resources"):
        ossie_datasets: list[OssieDataset] = []
        ossie_metrics: list[OssieMetric] = []
        ossie_relationships: list[OssieRelationship] = []
        for resource in hex_project.resources:
            if resource.type == "model":
                hex_model = resource
                if conversion := convert_hex_model(hex_model, ctx=ctx):
                    dataset, metrics, relationships = conversion
                    ossie_datasets.append(dataset)
                    ossie_metrics.extend(metrics)
                    ossie_relationships.extend(relationships)
            elif resource.type == "view":
                hex_view = resource
                convert_hex_view(hex_view, ctx=ctx):
                
    ossie_semantic_model = OssieSemanticModel(
        name=hex_project.name,
        dialect=ctx.ossie_dialect,
        datasets=ossie_datasets,
        metrics=ossie_metrics,
        relationships=ossie_relationships,
    )
    ossie_document = OssieDocument(
        semantic_model=[ossie_semantic_model],
    )

    return ossie_document
