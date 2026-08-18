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

from types import SimpleNamespace

import pytest
from ossie import OSIDialect

from ossie_hex.hex_to_ossie.load_hex_project import load_hex_project
from ossie_hex.util.errors import ConversionError


def test_load_hex_project_uses_ossie_dialect() -> None:
    project = load_hex_project(
        {"orders.yml": "id: orders\nbase_sql_table: analytics.orders\n"},
        project_name="demo",
        dialect=OSIDialect.SNOWFLAKE,
    )

    assert project.dialect.root == "snowflake"


def test_load_hex_project_rejects_duplicate_ids() -> None:
    files = {
        "a.yml": "id: orders\nbase_sql_table: a.orders\n",
        "b.yml": "id: orders\nbase_sql_table: b.orders\n",
    }

    with pytest.raises(ConversionError, match="Duplicate Hex resource id 'orders'"):
        load_hex_project(files, project_name="demo")


def test_load_hex_project_raises_loader_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class LoaderProblem:
        severity = "error"

        def to_str(self) -> str:
            return "[ERROR] Broken resource"

    loader_result = SimpleNamespace(problems=[LoaderProblem()])

    monkeypatch.setattr(
        "ossie_hex.hex_to_ossie.load_hex_project.load_project_files",
        lambda **_kwargs: loader_result,
    )

    with pytest.raises(ConversionError, match=r"\[ERROR\] Broken resource"):
        load_hex_project({}, project_name="demo")
