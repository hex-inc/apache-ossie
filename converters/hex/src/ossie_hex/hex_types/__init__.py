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

import re

from hex_sl_utils.spec.types import (
    DEFAULT_RESOURCE_TYPE as DEFAULT_HEX_RESOURCE_TYPE,
)
from hex_sl_utils.spec.types import (
    DataType as HexDataType,
)
from hex_sl_utils.spec.types import (
    Dimension as HexDimension,
)
from hex_sl_utils.spec.types import (
    EntityId as HexID,
)
from hex_sl_utils.spec.types import (
    Measure as HexMeasure,
)
from hex_sl_utils.spec.types import (
    MeasureFuncName as HexMeasureFuncName,
)
from hex_sl_utils.spec.types import (
    Model as HexModel,
)
from hex_sl_utils.spec.types import (
    Project as HexProject,
)
from hex_sl_utils.spec.types import (
    Relation as HexRelation,
)
from hex_sl_utils.spec.types import (
    RelationType as HexRelationType,
)
from hex_sl_utils.spec.types import (
    Resource as HexResource,
)
from hex_sl_utils.spec.types import (
    ScalarExpression as HexScalarExpression,
)
from hex_sl_utils.spec.types import (
    ScalarExpressionDefaultBoolean as HexScalarExpressionDefaultBoolean,
)
from hex_sl_utils.spec.types import (
    ScalarExpressionDefaultNumber as HexScalarExpressionDefaultNumber,
)
from hex_sl_utils.spec.types import (
    SemiAdditive as HexSemiAdditive,
)
from hex_sl_utils.spec.types import (
    SemiAdditiveOverMember as HexSemiAdditiveOverMember,
)
from hex_sl_utils.spec.types import (
    View as HexView,
)
from hex_sl_utils.spec.types import (
    ViewContentDimensionItem as HexGroupDimension,
)
from hex_sl_utils.spec.types import (
    ViewContentMeasureItem as HexGroupMeasure,
)
from hex_sl_utils.spec.types import (
    ViewContentsGroup as HexGroup,
)
from hex_sl_utils.spec.types import (
    Visibility as HexVisibility,
)
from hex_sl_utils.spec.types import (
    id_to_name,
)
from hex_sl_utils.spec.types import (
    parse_resource as parse_hex_resource,
)

from .datatype_mapping import (
    HEX_TO_OSSIE,
    LOSSLESS_HEX_TYPES,
    OSSIE_TO_HEX,
    TEMPORAL_HEX_TYPES,
    is_lossless_hex_type,
    is_temporal_hex_type,
)
from .dialect_mapping import ossie_to_hex_dialect
from .hex_id import (
    HEX_ID_PATTERN,
    HEX_ID_RE,
    HEX_RESERVED_ID_PREFIX,
    HEX_RESERVED_IDS,
    normalize_to_hex_id,
)

DEFAULT_HEX_VISIBILITY = HexVisibility.PUBLIC
HEX_REF_PATTERN = r"\$\{\s*([^}]+?)\s*\}"
HEX_REF_RE = re.compile(HEX_REF_PATTERN)


def is_default_hex_visibility(visibility: HexVisibility) -> bool:
    return visibility == DEFAULT_HEX_VISIBILITY


__all__ = [
    "DEFAULT_HEX_RESOURCE_TYPE",
    "DEFAULT_HEX_VISIBILITY",
    "HEX_ID_PATTERN",
    "HEX_ID_RE",
    "HEX_REF_PATTERN",
    "HEX_REF_RE",
    "HEX_RESERVED_IDS",
    "HEX_RESERVED_ID_PREFIX",
    "HEX_TO_OSSIE",
    "LOSSLESS_HEX_TYPES",
    "OSSIE_TO_HEX",
    "TEMPORAL_HEX_TYPES",
    "HexDataType",
    "HexDimension",
    "HexGroup",
    "HexGroupDimension",
    "HexGroupMeasure",
    "HexID",
    "HexMeasure",
    "HexMeasureFuncName",
    "HexModel",
    "HexProject",
    "HexRelation",
    "HexRelationType",
    "HexResource",
    "HexScalarExpression",
    "HexScalarExpressionDefaultBoolean",
    "HexScalarExpressionDefaultNumber",
    "HexSemiAdditive",
    "HexSemiAdditiveOverMember",
    "HexView",
    "HexVisibility",
    "id_to_name",
    "is_default_hex_visibility",
    "is_lossless_hex_type",
    "is_temporal_hex_type",
    "normalize_to_hex_id",
    "ossie_to_hex_dialect",
    "parse_hex_resource",
]
