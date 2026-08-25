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

import pytest
from ossie import OSIDataType

from ossie_hex.hex import HexDataType
from ossie_hex.ossie_to_hex.convert_ossie_datatype import convert_ossie_datatype


@pytest.mark.parametrize(
    ("ossie_datatype", "hex_datatype"),
    [
        (OSIDataType.STRING, HexDataType.STRING),
        (OSIDataType.INTEGER, HexDataType.NUMBER),
        (OSIDataType.DECIMAL, HexDataType.NUMBER),
        (OSIDataType.FLOAT, HexDataType.NUMBER),
        (OSIDataType.BOOLEAN, HexDataType.BOOLEAN),
        (OSIDataType.DATE, HexDataType.DATE),
        (OSIDataType.DATE_TIME, HexDataType.TIMESTAMP_NAIVE),
        (OSIDataType.DATE_TIME_TZ, HexDataType.TIMESTAMP_TZ),
        (OSIDataType.TIME, HexDataType.OTHER),
        (OSIDataType.OPAQUE, HexDataType.OTHER),
    ],
)
def test_maps_datatype(
    ossie_datatype: OSIDataType,
    hex_datatype: HexDataType,
) -> None:
    result = convert_ossie_datatype(ossie_datatype, HexDataType.STRING)
    assert result == hex_datatype


def test_uses_default_when_missing() -> None:
    default = HexDataType.BOOLEAN
    result = convert_ossie_datatype(None, default)
    assert result == default
