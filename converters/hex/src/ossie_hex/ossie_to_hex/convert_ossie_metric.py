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

from typing import Any

from ossie import OSIMetric

from ..hex import HexDataType, HexMeasure
from .context import ExportContext
from .convert_ossie_datatype import convert_ossie_datatype
from .convert_ossie_expression import convert_ossie_expression
from .convert_ossie_name import convert_ossie_name


def convert_ossie_metric(
    ossie_metric: OSIMetric,
    *,
    ctx: ExportContext,
) -> HexMeasure | None:
    with ctx.problem_scope(ossie_metric.name):
        spec: dict[str, Any] = {}

        with ctx.problem_scope("name"):
            hex_entity_id = convert_ossie_name(ossie_metric.name, ctx=ctx)
            if hex_entity_id is None:
                return None
            spec["id"] = hex_entity_id

        if ossie_metric.description:
            spec["description"] = ossie_metric.description

        with ctx.problem_scope("datatype"):
            spec["type"] = convert_ossie_datatype(
                ossie_metric.datatype, HexDataType.NUMBER
            )

        with ctx.problem_scope("expression"):
            # Since a metric expression can contain references to fields on datasets, those
            # references need to be converted to the corresponding Hex IDs and syntax.
            resolve = None  # TODO: implement

            func_sql = convert_ossie_expression(
                ossie_metric.expression,
                resolve=resolve,
                ctx=ctx,
            )
            spec["func_sql"] = func_sql

        with ctx.problem_scope("ai_context"):
            if ossie_metric.ai_context is not None:
                ctx.warn("Not supported")

        with ctx.problem_scope("custom_extensions"):
            if ossie_metric.custom_extensions is not None:
                ctx.warn("Not supported")

        # Attributes not set:
        # - HexMeasure.name: Ossie does not encode a display name
        # - HexMeasure.visibility: Ossie does not support this concept
        # - HexMeasure.func_calc: Ossie does not express Hex calculation language

        return HexMeasure(**spec)
