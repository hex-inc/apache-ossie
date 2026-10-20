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

from collections.abc import Mapping

from ossie import OssieDataType

from ..hex import HexDataType
from .context import ImportContext

_DATATYPE_MAP: Mapping[HexDataType, OssieDataType] = {
    HexDataType.NUMBER: OssieDataType.DECIMAL,  # ambiguous
    HexDataType.STRING: OssieDataType.STRING,
    HexDataType.TIMESTAMP_TZ: OssieDataType.DATE_TIME_TZ,
    HexDataType.TIMESTAMP_NAIVE: OssieDataType.DATE_TIME,
    HexDataType.DATE: OssieDataType.DATE,
    HexDataType.BOOLEAN: OssieDataType.BOOLEAN,
    HexDataType.NULL: OssieDataType.OPAQUE,  # Ossie has no null datatype
    HexDataType.OTHER: OssieDataType.OPAQUE,  # Ossie has no other datatype
}


def convert_hex_datatype(
    hex_datatype: HexDataType | None,
    *,
    ctx: ImportContext,
) -> OssieDataType:
    """Map an Ossie datatype to a Hex type."""
    if hex_datatype is HexDataType.NUMBER:
        ctx.warn("Ambiguous", code="hex-datatype-number")
    ossie_datatype = _DATATYPE_MAP.get(hex_datatype)
    if ossie_datatype is None:
        ctx.fatal(
            f"Unexpected datatype value: {hex_datatype}. Using Opaque Ossie datatype instead.",
            internal_message="Should have been validated in the load phase to be one of HexDataType values.",
        )
        return OssieDataType.OPAQUE
    return ossie_datatype
