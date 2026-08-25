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

from ossie import OSISemanticModel

from ..hex import HexModel
from .context import ExportContext
from .convert_ossie_dataset import convert_ossie_dataset
from .convert_ossie_metric import convert_ossie_metric
from .convert_ossie_relationship import convert_ossie_relationship


def convert_ossie_semantic_model(
    ossie_semantic_model: OSISemanticModel,
    *,
    ctx: ExportContext,
) -> list[HexModel]:
    """Convert an Ossie semantic model to Hex models.

    Returns the converted Hex models.
    """
    with ctx.problem_scope(ossie_semantic_model.name):
        hex_models: list[HexModel] = []
        with ctx.problem_scope("datasets"):
            for ossie_dataset in ossie_semantic_model.datasets:
                if hex_model := convert_ossie_dataset(ossie_dataset, ctx=ctx):
                    hex_models.append(hex_model)

        with ctx.problem_scope("metrics"):
            for ossie_metric in ossie_semantic_model.metrics or []:
                convert_ossie_metric(ossie_metric, ctx=ctx)

        with ctx.problem_scope("relationships"):
            for ossie_relationship in ossie_semantic_model.relationships or []:
                convert_ossie_relationship(ossie_relationship, ctx=ctx)

    return hex_models
