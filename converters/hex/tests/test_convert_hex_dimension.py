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

import yaml
from ossie import OSIDialect

from ossie_hex.cli.hex_project_io import read_hex_project
from ossie_hex.hex_to_ossie import convert_hex_to_ossie
from tests.utils import hex_extension


def test_hex_dimension_with_expr_calc_is_preserved(
    calc_dimension_hex_path: str,
) -> None:
    """A Hex formula names other fields, which an Ossie expression cannot do."""
    files = read_hex_project(calc_dimension_hex_path)
    yaml_text, warnings = convert_hex_to_ossie(
        files,
        dialect=OSIDialect.ANSI_SQL,
        model_name="demo",
    )
    dataset = yaml.safe_load(yaml_text)["semantic_model"][0]["datasets"][0]

    assert [field["name"] for field in dataset["fields"]] == [
        "first_name",
        "last_name",
    ]

    payload = hex_extension(dataset)
    assert payload is not None
    (preserved,) = payload["dimensions"]
    assert preserved["id"] == "full_name"
    assert preserved["expr_calc"] == "Concat(first_name, ' ', last_name)"
    assert any("full_name" in w.message for w in warnings)


def test_preserves_lossy_types(tmp_path: Path) -> None:
    """Some Hex types have no Ossie datatype, so the custom extension must hold them."""

    # "label" is a control
    (tmp_path / "events.yml").write_text(
        """
id: events
base_sql_table: s.events
dimensions:
- id: nothing
  type: 'null'
- id: label
  type: string
""",
        encoding="utf-8",
    )

    files = read_hex_project(tmp_path)
    yaml_text, _ = convert_hex_to_ossie(
        files,
        dialect=OSIDialect.ANSI_SQL,
        model_name="demo",
    )
    fields = yaml.safe_load(yaml_text)["semantic_model"][0]["datasets"][0]["fields"]
    nothing, label = fields

    assert nothing["datatype"] == "Opaque"
    assert hex_extension(nothing) == {"type": "null"}

    assert label["datatype"] == "String"
    assert hex_extension(label) is None
