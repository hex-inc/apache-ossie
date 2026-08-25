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

import pytest
from inline_snapshot import snapshot

from ossie_hex.hex import HexDialect, HexModel, HexProject
from ossie_hex.ossie_to_hex.context import ExportContext
from ossie_hex.ossie_to_hex.dump_hex_project import dump_hex_project


@pytest.fixture
def foo() -> HexProject:
    return HexProject(
        name="foo",
        dialect=HexDialect("duckdb"),
        resources=[
            HexModel(id="bar", base_sql_table="public.bar"),
            HexModel(id="baz", base_sql_table="public.baz"),
        ],
    )


@pytest.fixture
def ctx() -> ExportContext:
    return ExportContext()


def test_writes_resource_files(
    ctx: ExportContext, foo: HexProject, tmp_path: Path
) -> None:
    project_dir = tmp_path / "out"
    dump_hex_project(foo, project_dir=project_dir, ctx=ctx)
    assert (project_dir / "bar.yml").read_text(encoding="utf-8") == snapshot(
        """\
id: bar
base_sql_table: public.bar
"""
    )
    assert (project_dir / "baz.yml").read_text(encoding="utf-8") == snapshot(
        """\
id: baz
base_sql_table: public.baz
"""
    )
    assert not ctx.problems


def test_creates_project_dir_when_missing(ctx: ExportContext, tmp_path: Path) -> None:
    project = HexProject(name="foo", dialect=HexDialect("duckdb"), resources=[])
    project_dir = tmp_path / "nested" / "out"
    dump_hex_project(project, project_dir=str(project_dir), ctx=ctx)
    assert project_dir.is_dir()
    assert list(project_dir.iterdir()) == []
    assert not ctx.problems


def test_resolves_project_dir(
    ctx: ExportContext, foo: HexProject, tmp_path: Path
) -> None:
    project_dir = tmp_path / "nested" / ".." / "out"
    dump_hex_project(foo, project_dir=project_dir, ctx=ctx)
    resolved = (tmp_path / "out").resolve()
    assert (resolved / "bar.yml").is_file()
    assert not (tmp_path / "nested").exists()
    assert not ctx.problems
