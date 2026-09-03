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

from syrupy.assertion import SnapshotAssertion

from ossie_hex.ossie_to_hex import convert_ossie_to_hex
from tests.utils import problems_snapshot

REPO_ROOT = Path(__file__).resolve().parents[4]
VENDOR_ROOT = REPO_ROOT / "converters"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _snapshot_directory(path: Path) -> str:
    sections = []
    for file_path in sorted(path.rglob("*")):
        if file_path.is_file():
            relative_path = file_path.relative_to(path).as_posix()
            sections.append(f"--- {relative_path} ---\n{read_text(file_path).rstrip()}")
    return "\n\n".join(sections) + "\n"


def assert_vendor_to_hex(
    ossie_yaml: str,
    *,
    dialect: str | None,
    snapshot: SnapshotAssertion,
    tmp_path: Path,
) -> None:
    ossie_path = tmp_path / "model.ossie.yaml"
    output_path = tmp_path / "hex"
    ossie_path.write_text(ossie_yaml, encoding="utf-8")

    hex_projects, problems = convert_ossie_to_hex(
        ossie_path,
        output_path,
        dialect=dialect,
    )

    assert len(hex_projects) == 1
    assert not any(problem.severity == "fatal" for problem in problems)
    assert _snapshot_directory(output_path) == snapshot(name="hex_files")
    assert problems_snapshot(problems, include_causes=True) == snapshot(name="problems")
