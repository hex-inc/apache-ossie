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

from collections.abc import Mapping

from ossie import OssieDialect

from ..hex import (
    HexCanonicalDialectName,
    HexDialectName,
    normalize_hex_dialect_name,
)
from .context import ImportContext

_DIALECT_NAME_MAP: Mapping[HexCanonicalDialectName, OssieDialect | None] = {
    "bigquery": OssieDialect.BIGQUERY,
    "clickhouse": OssieDialect.ANSI_SQL,
    "duckdb": OssieDialect.ANSI_SQL,
    "mssql": OssieDialect.ANSI_SQL,
    "mysql": OssieDialect.ANSI_SQL,
    "postgres": OssieDialect.POSTGRES,
    "redshift": OssieDialect.ANSI_SQL,
    "snowflake": OssieDialect.SNOWFLAKE,
    "spark": OssieDialect.DATABRICKS,
    "trino": OssieDialect.ANSI_SQL,
}


def convert_hex_dialect(
    hex_dialect_name: HexDialectName,
    *,
    _ctx: ImportContext,
) -> OssieDialect:
    """Convert a Hex dialect name to an Ossie dialect."""
    hex_canonical_dialect_name = normalize_hex_dialect_name(hex_dialect_name)
    ossie_dialect = _DIALECT_NAME_MAP.get(hex_canonical_dialect_name)
    return ossie_dialect
