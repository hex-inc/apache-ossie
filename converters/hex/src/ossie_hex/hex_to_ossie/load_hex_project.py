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

from hex_sl_utils.spec.load import load_project_files
from ossie import OSIDialect

from ..hex_types import HexProject, ossie_to_hex_dialect
from ..util.errors import ConversionError


def load_hex_project(
    files: dict[str, str],
    *,
    project_name: str,
    dialect: OSIDialect = OSIDialect.ANSI_SQL,
) -> HexProject:
    """Interpret files as a Hex project.

    ``files`` a mapping of file names to contents text.
    ``project_name`` a name for the project.

    Returns a `HexProject`.
    """
    loaded = load_project_files(
        files=files,
        project_name=project_name,
        dialect_name=ossie_to_hex_dialect(dialect),
    )
    errors = [
        problem for problem in loaded.problems if problem.severity in {"fatal", "error"}
    ]
    if errors:
        raise ConversionError("\n\n".join(problem.to_str() for problem in errors))

    seen_ids: set[str] = set()
    for resource in loaded.project.resources:
        if resource.id in seen_ids:
            raise ConversionError(f"Duplicate Hex resource id '{resource.id}'")
        seen_ids.add(resource.id)

    return loaded.project
