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


class ConvertOssieCtx:
    """State shared throughout one Ossie-to-Hex conversion."""

    def __init__(self) -> None:
        self.warnings: list[ConversionWarning] = []
        self._ossie_dialect: OSIDialect | None = None

    @property
    def ossie_dialect(self) -> OSIDialect:
        if self._ossie_dialect is None:
            raise ValueError("No Ossie dialect has been selected")
        return self._ossie_dialect

    def warn(self, message: str) -> None:
        self.warnings.append(ConversionWarning(message))

    def set_ossie_dialect(self, dialect: OSIDialect) -> None:
        if self._ossie_dialect is not None:
            raise RuntimeError("An Ossie dialect has already been selected")
        self._ossie_dialect = dialect
