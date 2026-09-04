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

from pathlib import Path

from ossie import OssieDocument

from ..hex import HexDialectName, load_hex_project
from ..util.problem import Problem
from .context import ImportContext
from .convert_hex_dialect import convert_hex_dialect
from .convert_hex_project import convert_hex_project
from .dump_ossie_document import dump_ossie_document
from .load_hex_dialect import load_hex_dialect


def convert_hex_to_ossie(
    input: Path | str,
    output: Path | str | None = None,
    *,
    dialect: HexDialectName | None = None,
    name: str | None = None,
    description: str | None = None,
) -> tuple[OssieDocument, list[Problem]]:
    """Convert a Hex semantic project to an Ossie document.

    Args:
        - `input`: A path to the Hex semantic project directory.
        - `output`: Optional. A path to the desired output file. If not provided,
          the output is not written to a file.
        - `dialect`: Optional. A SQL engine dialect to interpret expressions in. If not
          provided, the default SQLGlot dialect will be used.
        - `name`: Optional. A name for the project. If not provided, the name of
          the input directory will be used.
        - `description`: Optional. A human-readable description of the project.

    Returns: a tuple of:
        - `ossie_document`: An Ossie document.
        - `problems`: A list of problems encountered.
    """
    ctx = ImportContext()

    with ctx.phase_scope("load"):
        hex_project = load_hex_project(
            project_dir=input, project_name=name, dialect_name=dialect, ctx=ctx
        )
        hex_dialect = load_hex_dialect(dialect, ctx=ctx)

    with ctx.phase_scope("convert"):
        ossie_dialect = convert_hex_dialect(hex_dialect, ctx=ctx)
        ctx.set_dialects(hex_dialect, ossie_dialect)
        ossie_document = convert_hex_project(
            hex_project,
            description=description,
            ctx=ctx,
        )

    with ctx.phase_scope("dump"):
        if output is not None:
            output = Path(output).resolve()
            output.mkdir(parents=True, exist_ok=True)
            dump_ossie_document(ossie_document, path=output, ctx=ctx)

    return ossie_document, ctx.problems
