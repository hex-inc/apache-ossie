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

from ossie import OssieField

from ..hex import HexDimension
from .context import ImportContext
from .convert_hex_datatype import convert_hex_datatype
from .convert_hex_scalar_expression import convert_hex_scalar_expression


def convert_hex_dimension(
    hex_dimension: HexDimension,
    *,
    ctx: ImportContext,
) -> OssieField | None:
    with ctx.problem_scope(hex_dimension.id):
        f_name = hex_dimension.id
        f_description = hex_dimension.description or None

        with ctx.problem_scope("name"):
            # `OssieField.label` is described by the spec as "label for categorization". that
            # doesn't seem it's a display name, but other converters use it as such, so
            # we'll do the same for now.
            f_label = hex_dimension.name or None
            ctx.warn("Not supported", code="hex-name")

        with ctx.problem_scope("type"):
            f_datatype = convert_hex_datatype(hex_dimension.type, ctx=ctx)

        f_expression = convert_hex_scalar_expression(hex_dimension.expr_sql, ctx=ctx)

        # `HexDimension.unique` is handled by `HexModel` conversion

        if f_expression is None:
            return None

        return OssieField(
            name=f_name,
            expression=f_expression,
            label=f_label,
            description=f_description,
            datatype=f_datatype,
            # attributes not set:
            # - dimension: Hex does not support temporal designations for non-temporal types
            # - ai_context: Hex does not encode this concept
            # - custom_extensions: Hex does not support this concept
        )
