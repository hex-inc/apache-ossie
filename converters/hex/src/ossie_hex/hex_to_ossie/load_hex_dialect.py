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

from typing import assert_never

from ..hex import HexDialectName
from .context import ExportContext


def load_hex_dialect(
    hex_dialect_name: HexDialectName | str | None,
    *,
    ctx: ExportContext,
) -> HexDialectName:
    if isinstance(hex_dialect_name, HexDialectName):
        return hex_dialect_name
    elif isinstance(hex_dialect_name, str):
        value = hex_dialect_name.lower()
        return HexDialectName(value)
    elif hex_dialect_name is None:
        ctx.info(
            "No Hex dialect specified; using DuckDB",
            code="missing-dialect",
        )
        return "duckdb"
    else:
        assert_never(hex_dialect_name)
