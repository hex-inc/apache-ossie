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
from inline_snapshot import snapshot
from ossie import (
    OSIAIContextObject,
    OSICustomExtension,
    OSIDialect,
)

from ossie_hex.hex import HexDataType, HexDialect
from ossie_hex.ossie_to_hex.context import ExportContext
from ossie_hex.ossie_to_hex.convert_ossie_metric import convert_ossie_metric
from tests.ossie_to_hex.utils import Quick
from tests.utils import problems_snapshot


@pytest.fixture
def ctx() -> ExportContext:
    ctx = ExportContext()
    ctx.set_dialects(
        ossie_dialect=OSIDialect.ANSI_SQL, hex_dialect=HexDialect("duckdb")
    )
    return ctx


def test_preserve_name(ctx: ExportContext) -> None:
    name = "foo"
    foo = Quick.metric(name, "Integer", [("ANSI_SQL", "foo")])
    result = convert_ossie_metric(foo, ctx=ctx)
    assert result is not None
    assert result.id == name
    assert not ctx.problems


def test_preserve_description(ctx: ExportContext) -> None:
    description = "Foo bar baz"
    foo = Quick.metric("foo", "Integer", [("ANSI_SQL", "foo")], description=description)
    result = convert_ossie_metric(foo, ctx=ctx)
    assert result is not None
    assert result.description == description
    assert not ctx.problems


def test_defaults_to_number_datatype(ctx: ExportContext) -> None:
    datatype = None
    foo = Quick.metric("foo", datatype, [("ANSI_SQL", "foo")])
    result = convert_ossie_metric(foo, ctx=ctx)
    assert result is not None
    assert result.type == HexDataType.NUMBER
    assert not ctx.problems


def test_warns_about_ai_context_str(ctx: ExportContext) -> None:
    ai_context = "bar"
    foo = Quick.metric("foo", "Integer", [("ANSI_SQL", "foo")], ai_context=ai_context)
    convert_ossie_metric(foo, ctx=ctx)
    assert problems_snapshot(ctx.problems) == snapshot("[WARNING] Not supported")


def test_warns_about_ai_context_obj(ctx: ExportContext) -> None:
    ai_context = OSIAIContextObject(synonyms=("bar", "baz"))
    foo = Quick.metric("foo", "Integer", [("ANSI_SQL", "foo")], ai_context=ai_context)
    convert_ossie_metric(foo, ctx=ctx)
    assert problems_snapshot(ctx.problems) == snapshot("[WARNING] Not supported")


def test_warns_about_custom_extensions(ctx: ExportContext) -> None:
    custom_extension = OSICustomExtension(vendor_name="foo", data="bar")
    foo = Quick.metric(
        "foo",
        "Integer",
        [("ANSI_SQL", "foo")],
        custom_extensions=[custom_extension],
    )
    convert_ossie_metric(foo, ctx=ctx)
    assert problems_snapshot(ctx.problems) == snapshot("[WARNING] Not supported")


def test_converts_expression(ctx: ExportContext) -> None:
    foo = Quick.metric("foo", "Integer", [("ANSI_SQL", "foo")])
    result = convert_ossie_metric(foo, ctx=ctx)
    assert result is not None
    assert result.func_sql == snapshot("foo")
    assert not ctx.problems
