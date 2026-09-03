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

from pathlib import Path

from osi_omni.omni_to_osi import convert_omni_to_osi
from syrupy.assertion import SnapshotAssertion

from tests.vendor.utils import VENDOR_ROOT, assert_vendor_to_hex, read_text

FIXTURE = VENDOR_ROOT / "omni" / "tests" / "fixtures" / "tpcds_omni"


def test_omni_tpcds_to_hex(
    snapshot: SnapshotAssertion,
    tmp_path: Path,
) -> None:
    omni_files = {
        path.relative_to(FIXTURE).as_posix(): read_text(path)
        for path in sorted(FIXTURE.rglob("*"))
        if path.is_file()
    }
    assert_vendor_to_hex(
        convert_omni_to_osi(omni_files),
        dialect=None,
        snapshot=snapshot,
        tmp_path=tmp_path,
    )
