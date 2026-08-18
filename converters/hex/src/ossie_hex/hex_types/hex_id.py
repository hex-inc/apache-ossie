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

import re

from hex_sl_utils.spec.types import (
    ID_PATTERN as HEX_ID_PATTERN,
)
from hex_sl_utils.spec.types import (
    RESERVED_ID_PREFIX as HEX_RESERVED_ID_PREFIX,
)
from hex_sl_utils.spec.types import (
    RESERVED_IDS as HEX_RESERVED_IDS,
)

from ..util.errors import ConversionError

HEX_ID_RE = re.compile(HEX_ID_PATTERN)


def normalize_to_hex_id(name: str, what: str, taken: set[str]) -> str:
    """Coerce an Ossie name into a Hex ID.

    Collisions and blank names are errors.
    """
    if not name.strip():
        raise ConversionError(f"{what} has a blank name; name it in the Ossie model.")
    raw = name
    if HEX_ID_RE.match(raw):
        # preserve valid Hex ID's
        out = raw
    else:
        # lowercase; replace invalid characters with underscores; remove
        # leading/trailing underscores
        out = re.sub(r"[^a-z0-9_]+", "_", raw.lower()).strip("_")
        if not out:
            out = "_1"
        elif out[0].isdigit():
            out = f"_{out}"
        if len(out) < 2:
            out = f"{out}_"
        if len(out) > 128:
            out = out[:128]
    if out in taken:
        raise ConversionError(
            f"{what} '{name}' coerces to '{out}', which collides with another "
            f"name; rename it in the Ossie model."
        )
    if out.startswith(HEX_RESERVED_ID_PREFIX) or out in HEX_RESERVED_IDS:
        raise ConversionError(f"{what} '{name}' coerced to reserved Hex ID '{out}'")
    taken.add(out)
    return out
