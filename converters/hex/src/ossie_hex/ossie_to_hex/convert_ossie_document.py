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

from ossie import OSIDocument

from ..hex import HexDialect, HexModel, HexProject, HexResource
from .context import ExportContext
from .convert_ossie_semantic_model import convert_ossie_semantic_model


def convert_ossie_document(
    ossie_document: OSIDocument | None,
    *,
    hex_dialect: HexDialect,
    hex_project_name: str,
    ctx: ExportContext,
) -> HexProject:
    """Convert an Ossie document to a Hex semantic project.

    Returns the converted Hex project.
    """
    hex_models: list[HexModel] = []
    if ossie_document is not None:
        for ossie_semantic_model in ossie_document.semantic_model:
            with ctx.problem_scope("semantic_model"):
                hex_models_ = convert_ossie_semantic_model(
                    ossie_semantic_model, ctx=ctx
                )
                hex_models.extend(hex_models_)

    hex_resources: list[HexResource] = []
    hex_resources.extend(hex_models)

    hex_project = HexProject(
        name=hex_project_name,
        dialect=hex_dialect,
        resources=hex_resources,
    )

    return hex_project
