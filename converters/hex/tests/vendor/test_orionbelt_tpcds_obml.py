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

import sys
from pathlib import Path

import pytest
import yaml
from syrupy.assertion import SnapshotAssertion

from tests.vendor.utils import VENDOR_ROOT, assert_vendor_to_hex, read_text

FIXTURE = VENDOR_ROOT / "orionbelt" / "tests" / "fixtures" / "tpcds_as_obml.yaml"


@pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason="The OrionBelt converter requires Python 3.12 or newer",
)
def test_orionbelt_tpcds_obml_to_hex(
    snapshot: SnapshotAssertion,
    tmp_path: Path,
) -> None:
    from ossie_orionbelt import OBMLtoOSI

    obml = yaml.safe_load(read_text(FIXTURE))
    ossie = OBMLtoOSI(obml).convert()
    assert_vendor_to_hex(
        yaml.safe_dump(ossie, sort_keys=False),
        dialect=None,
        snapshot=snapshot,
        tmp_path=tmp_path,
    )
