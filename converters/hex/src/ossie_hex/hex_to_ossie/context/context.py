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

import logging

from hex_sl_utils.dialect.dialect import Dialect as HexDialect
from ossie import OssieDialect

from ossie_hex.ossie import OssieDialectName

from ...hex import HexDialectName
from ...util.context import Context
from .problem_code import ImportProblemCode

logger = logging.getLogger(__name__)


class ImportContext(Context[ImportProblemCode]):
    """Context for importing from Hex specification to Ossie specification."""

    # global scope
    hex_dialect: HexDialect
    ossie_dialect: OssieDialect

    def __init__(self) -> None:
        super().__init__(logger=logger)

    def set_dialects(
        self,
        hex_dialect: HexDialect | HexDialectName,
        ossie_dialect: OssieDialect | OssieDialectName,
    ) -> None:
        self.hex_dialect = (
            hex_dialect
            if isinstance(hex_dialect, HexDialect)
            else HexDialect.from_name(hex_dialect)
        )
        self.ossie_dialect = (
            ossie_dialect
            if isinstance(ossie_dialect, OssieDialect)
            else OssieDialect(ossie_dialect)
        )
