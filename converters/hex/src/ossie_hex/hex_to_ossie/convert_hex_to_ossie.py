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

from ossie import OSIDialect

from ..util.errors import ConversionWarning
from ..util.yaml import dump_yaml
from .context import ConvertHexCtx
from .convert_hex_project import convert_hex_project
from .load_hex_project import load_hex_project


def convert_hex_to_ossie(
    files: dict[str, str],
    *,
    dialect: OSIDialect,
    model_name: str,
) -> tuple[str, list[ConversionWarning]]:
    """Convert Hex project files to an Ossie file.

    ``files`` a mapping of file names to contents.
    ``dialect`` is the Ossie dialect that the Hex project's SQL is written in
        (a Hex project does not record one, so it has to be supplied by the
        caller). The converted expressions are tagged with it.
    ``model_name`` names the Ossie semantic model.

    Returns ``(ossie_text, warnings)``.
    """
    ctx = ConvertHexCtx(ossie_dialect=dialect)
    hex_project = load_hex_project(files, project_name=model_name)
    document, warnings = convert_hex_project(hex_project, ctx=ctx)
    data = document.model_dump(by_alias=True, exclude_none=True, mode="json")
    return dump_yaml(data), warnings
