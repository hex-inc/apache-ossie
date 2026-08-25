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

from __future__ import annotations

from ossie import (
    OSIDataType,
    OSIDialect,
    OSIDialectExpression,
    OSIExpression,
    OSIMetric,
)

from ..hex_extension import HEX_VENDOR, HexMeasureStash, maybe_write_extension
from ..hex_types import (
    HexDataType,
    HexMeasure,
    HexMeasureFuncName,
    HexScalarExpressionDefaultBoolean,
    HexScalarExpressionDefaultNumber,
)
from ..util.errors import ConversionError
from .context import ConvertHexCtx
from .convert_hex_datatype import hex_to_ossie_datatype
from .convert_hex_ref import qualify_hex_ref, rewrite_hex_refs

_FUNC_SQL: dict[HexMeasureFuncName, str] = {
    HexMeasureFuncName.COUNT: "COUNT",
    HexMeasureFuncName.COUNT_DISTINCT: "COUNT",
    HexMeasureFuncName.SUM: "SUM",
    HexMeasureFuncName.SUM_BOOLEAN: "SUM",
    HexMeasureFuncName.AVG: "AVG",
    HexMeasureFuncName.MIN: "MIN",
    HexMeasureFuncName.MAX: "MAX",
    HexMeasureFuncName.MEDIAN: "MEDIAN",
    HexMeasureFuncName.STDDEV: "STDDEV",
    HexMeasureFuncName.STDDEV_POP: "STDDEV_POP",
    HexMeasureFuncName.VARIANCE: "VARIANCE",
    HexMeasureFuncName.VARIANCE_POP: "VARIANCE_POP",
}


def convert_hex_measure(
    measure: HexMeasure,
    *,
    ctx: ConvertHexCtx,
) -> tuple[OSIMetric | None, HexMeasure | None]:
    """Compile a Hex measure into an Ossie metric.

    Returns either the metric or, for a measure Ossie cannot express, the
    measure itself for its dataset to preserve whole. A formula measure takes
    the latter path: it names other measures, which a metric being a SQL
    expression over fields cannot do, and there is nothing faithful to compile
    it into. Returning early also leaves its ID out of ``metric_names``, since
    it claims no metric name for a later measure to collide with.
    """
    expression_sql: str
    if measure.func_calc:
        ctx.warn(
            f"measure '{ctx.model_id}.{measure.id}' is a formula over other "
            f"measures, which an Ossie metric cannot express; no metric "
            f"was exported and the measure is preserved whole in "
            f"custom_extensions[{HEX_VENDOR}]"
        )
        return None, measure
    elif measure.func_sql:
        expression_sql = rewrite_hex_refs(measure.func_sql, ctx=ctx)
    elif measure.func:
        expression_sql = compile_func_measure(measure, ctx=ctx)
    else:
        raise ConversionError(
            f"measure '{ctx.model_id}.{measure.id}' has no aggregation definition"
        )

    metric_name = ctx.claim_metric_name(measure.id)
    if metric_name != measure.id:
        ctx.warn(
            f"measure '{measure.id}' on '{ctx.model_id}' collided with another "
            f"metric name; exported as '{metric_name}'"
        )

    stash = HexMeasureStash(
        model_id=ctx.model_id,
        measure_id=measure.id if metric_name != measure.id else None,
        display_name=measure.name,
        type=measure.type,
        visibility=measure.visibility,
        semi_additive=measure.semi_additive,
    )
    if measure.semi_additive is not None:
        ctx.warn(
            f"measure '{ctx.model_id}.{measure.id}' is semi-additive; "
            f"structure preserved in custom_extensions[{HEX_VENDOR}]"
        )

    datatype = convert_hex_measure_type(measure, ctx=ctx)

    metric = OSIMetric(
        name=metric_name,
        expression=OSIExpression(
            dialects=[
                OSIDialectExpression(
                    dialect=ctx.ossie_dialect,
                    expression=expression_sql,
                )
            ]
        ),
        description=measure.description or None,
        datatype=datatype,
        custom_extensions=maybe_write_extension(stash),
    )
    return metric, None


def compile_func_measure(measure: HexMeasure, *, ctx: ConvertHexCtx) -> str:
    """Compile a Hex ``func``/``of``/``filters`` measure into aggregate SQL."""
    if measure.func is None:
        raise ConversionError(
            f"measure '{ctx.model_id}.{measure.id}' has no aggregation function"
        )

    filters_sql = compile_filters(measure.filters, ctx=ctx)

    if measure.func == HexMeasureFuncName.COUNT and measure.of is None:
        if filters_sql:
            return f"COUNT(CASE WHEN {filters_sql} THEN 1 END)"
        return f"COUNT({ctx.model_id}.*)"

    target = compile_of(measure.of, ctx=ctx)
    if measure.func == HexMeasureFuncName.COUNT_DISTINCT:
        if filters_sql:
            return f"COUNT(DISTINCT CASE WHEN {filters_sql} THEN {target} END)"
        return f"COUNT(DISTINCT {target})"
    if measure.func == HexMeasureFuncName.SUM_BOOLEAN:
        body = f"CASE WHEN {target} THEN 1 ELSE 0 END"
        if filters_sql:
            return f"SUM(CASE WHEN {filters_sql} THEN {body} END)"
        return f"SUM({body})"

    func = _FUNC_SQL[measure.func]
    if filters_sql:
        return f"{func}(CASE WHEN {filters_sql} THEN {target} END)"
    return f"{func}({target})"


def compile_of(
    of_value: str | HexScalarExpressionDefaultNumber | None,
    *,
    ctx: ConvertHexCtx,
) -> str:
    """Compile the value a measure aggregates over into Ossie SQL."""
    if of_value is None:
        raise ConversionError("measure `of` is required for this aggregation")
    if isinstance(of_value, str):
        return qualify_hex_ref(of_value, ctx=ctx)
    if of_value.expr_calc:
        raise ConversionError(
            "inline `of` with expr_calc is not supported in Ossie SQL"
        )
    expr = of_value.expr_sql or ""
    return rewrite_hex_refs(expr, ctx=ctx)


def compile_filters(
    filters: list[str | HexScalarExpressionDefaultBoolean],
    *,
    ctx: ConvertHexCtx,
) -> str | None:
    """Compile a measure's filters into a single Ossie SQL predicate."""
    if not filters:
        return None
    parts: list[str] = []
    for filter in filters:
        if isinstance(filter, str):
            parts.append(qualify_hex_ref(filter, ctx=ctx))
        else:
            if filter.expr_calc:
                raise ConversionError(
                    "inline measure filter with expr_calc is not supported in Ossie SQL"
                )
            elif filter.expr_sql:
                parts.append(rewrite_hex_refs(filter.expr_sql, ctx=ctx))
            else:
                # should never happen
                raise ConversionError("Unexpected filter shape")
    return " AND ".join(parts)


def convert_hex_measure_type(
    measure: HexMeasure,
    *,
    ctx: ConvertHexCtx,
) -> OSIDataType:
    """Derive the Ossie data type for a Hex measure."""
    if measure.type != HexDataType.NUMBER:
        return hex_to_ossie_datatype(measure.type)

    # Hex has one numeric type, so retain Decimal unless the aggregate has a
    # fixed result type or the target dialect defines a more precise answer.
    if measure.func in (
        HexMeasureFuncName.COUNT,
        HexMeasureFuncName.COUNT_DISTINCT,
        HexMeasureFuncName.SUM_BOOLEAN,
    ):
        return OSIDataType.INTEGER
    elif measure.func in (
        HexMeasureFuncName.STDDEV,
        HexMeasureFuncName.STDDEV_POP,
    ):
        return OSIDataType.FLOAT
    elif measure.func in (
        HexMeasureFuncName.VARIANCE,
        HexMeasureFuncName.VARIANCE_POP,
    ):
        if ctx.ossie_dialect in (OSIDialect.BIGQUERY, OSIDialect.DATABRICKS):
            return OSIDataType.FLOAT
        else:
            pass
    elif measure.func == HexMeasureFuncName.MEDIAN:
        if ctx.ossie_dialect == OSIDialect.DATABRICKS:
            return OSIDataType.FLOAT
        else:
            pass

    return hex_to_ossie_datatype(measure.type)
