from collections.abc import Mapping
from typing import TypeAlias

from hex_sl_utils.calc import parse_calc_expression
from hex_sl_utils.calc.ast.args import Args
from hex_sl_utils.calc.ast.functions import (
    FuncAvg,
    FuncCount,
    FuncCountDistinct,
    FuncMax,
    FuncMedian,
    FuncMin,
    FuncStddev,
    FuncStddevPop,
    FuncSum,
    FuncSumBoolean,
    FuncVariance,
    FuncVariancePop,
)
from hex_sl_utils.datatype import DataType
from hex_sl_utils.datatype.datatype import DataType as HexSLUtilsDataType
from hex_sl_utils.expr import (
    ExpressionContext,
    ExpressionKind,
    TypedSelectExpression,
    rewrite_placeholder_references,
)
from hex_sl_utils.expr.expr_references import ResolveReference
from hex_sl_utils.spec.types import (
    ScalarExpression,
    ScalarExpressionDefaultBoolean,
    ScalarExpressionDefaultNumber,
)
from ossie import OssieDialectExpression, OssieExpression

from ossie_hex.util.parse_sql import exp, parse_one

from ..hex import HexAggregateExpression, HexAggregateFuncName, HexDataType
from .context import ImportContext


def convert_hex_aggregate_expression(
    hex_aggregate_expression: HexAggregateExpression,
    *,
    ctx: ImportContext,
) -> OssieExpression | None:
    if hex_aggregate_expression.func:
        sql_expression = _compile_func(
            func=hex_aggregate_expression.func,
            of=hex_aggregate_expression.of,
            filters=hex_aggregate_expression.filters,
            ctx=ctx,
        )
    elif hex_aggregate_expression.func_sql:
        with ctx.problem_scope("func_sql"):
            sql_expression = _compile_func_sql(
                func_sql=hex_aggregate_expression.func_sql,
                ctx=ctx,
            )
    elif hex_aggregate_expression.func_calc:
        with ctx.problem_scope("func_calc"):
            sql_expression = _compile_func_calc(
                func_calc=hex_aggregate_expression.func_calc,
                ctx=ctx,
            )
    else:
        ctx.fatal(
            "Unexpected aggregate expression shape.",
            internal_message="Should have been validated in the load phase to be one of func, func_sql, or func_calc",
        )
        return None

    if sql_expression is None:
        return None

    ossie_dialect_expression = OssieDialectExpression(
        dialect=ctx.ossie_dialect,
        expression=sql_expression,
    )
    ossie_expression = OssieExpression(
        dialects=[ossie_dialect_expression],
    )
    return ossie_expression


def _compile_func(
    func: HexAggregateFuncName,
    of: str | ScalarExpressionDefaultNumber | None,
    filters: list[str | ScalarExpressionDefaultBoolean] | None,
    *,
    ctx: ImportContext,
) -> str | None:
    """
    Compile a standard aggregation function.

    Args:
        func: A standard aggregation function name.
        of: The dimension over which the function is applied.
        filters: A list of boolean dimensions which must be true for a row to be included in the measure's aggregation.
        ctx: The import context.

    Returns:
        A compiled SQL expression, or None if the expression is invalid.
    """
    of_sql = _compile_of(of, ctx=ctx)
    filter_sql = _compile_filters(filters, ctx=ctx)
    agg_func = _compile_func_name(func, ctx=ctx)
    if of_sql is None or filter_sql is None:
        return None
    if filter_sql != "":
        arg_sql = f"CASE WHEN {filter_sql} THEN {of_sql} ELSE NULL END"
    else:
        arg_sql = of_sql
    arg_expr = TypedSelectExpression.from_sqlglot(
        parse_one(arg_sql, dialect=ctx.hex_dialect.sqlglot_dialect()),
        DataType.NUMBER,
    )
    compiled = agg_func.compile(
        arg_exprs=[arg_expr],
        dialect=ctx.hex_dialect,
        context=ExpressionContext.AGGREGATION,
        tz="UTC",
    )
    sql_expression = compiled.expression.sql(dialect=ctx.hex_dialect.sqlglot_dialect())
    return sql_expression


_Func: TypeAlias = (
    FuncAvg
    | FuncCount
    | FuncCountDistinct
    | FuncMax
    | FuncMedian
    | FuncMin
    | FuncStddev
    | FuncStddevPop
    | FuncSum
    | FuncSumBoolean
    | FuncVariance
    | FuncVariancePop
)

_FUNC_MAP: dict[HexAggregateFuncName, type[_Func]] = {
    HexAggregateFuncName.COUNT: FuncCount,
    HexAggregateFuncName.COUNT_DISTINCT: FuncCountDistinct,
    HexAggregateFuncName.SUM: FuncSum,
    HexAggregateFuncName.SUM_BOOLEAN: FuncSumBoolean,
    HexAggregateFuncName.AVG: FuncAvg,
    HexAggregateFuncName.MIN: FuncMin,
    HexAggregateFuncName.MAX: FuncMax,
    HexAggregateFuncName.MEDIAN: FuncMedian,
    HexAggregateFuncName.STDDEV: FuncStddev,
    HexAggregateFuncName.STDDEV_POP: FuncStddevPop,
    HexAggregateFuncName.VARIANCE: FuncVariance,
    HexAggregateFuncName.VARIANCE_POP: FuncVariancePop,
}


def _compile_func_name(
    func_name: HexAggregateFuncName,
    *,
    ctx: ImportContext,
) -> _Func:
    with ctx.problem_scope("func"):
        agg_func = _FUNC_MAP[func_name](args=Args(root=[]))
        return agg_func


def _compile_of(
    of: str | ScalarExpressionDefaultNumber | None,
    *,
    ctx: ImportContext,
) -> str | None:
    with ctx.problem_scope("of"):
        if of is None:
            sql_expression = "1"
        else:
            sql_expression = _compile_operand(
                of, ctx=ctx, context=ExpressionContext.PROJECTION
            )
        return sql_expression


def _compile_filters(
    filters: list[str | ScalarExpressionDefaultBoolean] | None,
    *,
    ctx: ImportContext,
) -> str | None:
    with ctx.problem_scope("filters"):
        if filters is None:
            return ""
        sql_expressions: list[str | None] = []
        for idx, filt in enumerate(filters):
            with ctx.problem_scope(idx):
                operand_sql = _compile_operand(
                    filt, ctx=ctx, context=ExpressionContext.WHERE
                )
                sql_expressions.append(operand_sql)
        if any(sql is None for sql in sql_expressions):
            return None
        if len(sql_expressions) == 0:
            return ""
        sql_expression = " AND ".join(f"({sql})" for sql in sql_expressions)
        return sql_expression


def _compile_operand(
    operand: str | ScalarExpression,
    *,
    ctx: ImportContext,
    context: ExpressionContext,
) -> str | None:
    if isinstance(operand, str):
        return _compile_func_sql("${" + operand + "}", ctx=ctx)
    elif operand.expr_sql:
        return _compile_func_sql(operand.expr_sql, ctx=ctx)
    elif operand.expr_calc:
        return _compile_func_calc(operand.expr_calc, ctx=ctx, context=context)
    else:
        ctx.fatal(
            "Unexpected scalar expression shape.",
            internal_message="Should have been validated in the load phase to be one of str, expr_sql, or expr_calc",
        )
        return None


def _compile_func_sql(
    func_sql: str,
    *,
    ctx: ImportContext,
) -> str:
    resolve = _build_resolve_reference(ctx=ctx)
    result = rewrite_placeholder_references(
        func_sql,
        resource=ctx.model.id,
        dialect=ctx.hex_dialect,
        resolve=resolve,
    )
    if result.unresolved_references:
        ctx.warn(
            f"Unresolved references in aggregate expression: {result.unresolved_references}",
        )
    return result.sql


def _compile_func_calc(
    func_calc: str,
    *,
    ctx: ImportContext,
    context: ExpressionContext = ExpressionContext.AGGREGATION,
) -> str:
    calc = parse_calc_expression(func_calc)
    columns = _build_columns(ctx=ctx)
    substitutions = _build_substitutions(ctx=ctx)
    typed_expr = ctx.hex_dialect.compile_calc_expr(
        expr=calc,
        context=context,
        columns=columns,
        substitutions=substitutions,
        timezone="UTC",
        parameters={},
        skip_mangle=True,
    )
    sql_expression = typed_expr.expression.sql(
        dialect=ctx.hex_dialect.sqlglot_dialect()
    )
    return sql_expression


_Columns: TypeAlias = Mapping[str, HexSLUtilsDataType]


def _build_columns(
    *,
    ctx: ImportContext,
) -> _Columns:
    # dimensions and measures are in scope for aggregate expressions
    m = ctx.model
    columns: _Columns = {}
    for d in m.dimensions:
        columns[d.id] = _datatype(d.type)
    for meas in m.measures:
        columns[meas.id] = _datatype(meas.type)
    # TODO: add relations? cross-dataset dimension references
    return columns


def _build_substitutions(
    *,
    ctx: ImportContext,
) -> dict[str, TypedSelectExpression]:
    p = ctx.project
    m = ctx.model
    substitutions: dict[str, TypedSelectExpression] = {}
    for r in m.relations:
        target = next(
            (foreign_m for foreign_m in p.models if foreign_m.id == r.target), None
        )
        if target is None:
            ctx.warn(
                f"Relation target model not found: {r.target}",
            )
            continue
        for d in target.dimensions:
            key = f"{r.id}.{d.id}"
            value = TypedSelectExpression(
                expression=exp.column(col=d.id, table=r.target, quoted=True),
                data_type=_datatype(d.type),
                kind=ExpressionKind.COLUMN,
            )
            substitutions[key] = value
        for meas in target.measures:
            key = f"{r.id}.{meas.id}"
            value = TypedSelectExpression(
                expression=exp.column(col=meas.id, table=r.target, quoted=True),
                data_type=_datatype(meas.type),
                kind=ExpressionKind.COLUMN,
            )
            substitutions[key] = value
    return substitutions


def _build_resolve_reference(*, ctx: ImportContext) -> ResolveReference:
    m = ctx.model
    p = ctx.project
    pairs: dict[tuple[str, str], tuple[str, str]] = {}
    for d in m.dimensions:
        pairs[(m.id, d.id)] = (m.id, d.id)
    for meas in m.measures:
        pairs[(m.id, meas.id)] = (m.id, meas.id)
    for r in m.relations:
        target = next(
            (foreign_m for foreign_m in p.models if foreign_m.id == r.target), None
        )
        if target is None:
            ctx.warn(
                f"Relation target model not found: {r.target}",
            )
            continue
        for d in target.dimensions:
            pairs[(r.id, d.id)] = (r.target, d.id)
        for meas in target.measures:
            pairs[(r.id, meas.id)] = (r.target, meas.id)
    resolve: ResolveReference = lambda resource, item: pairs.get((resource, item))
    return resolve


_DATATYPE_MAP: Mapping[HexDataType, HexSLUtilsDataType] = {
    HexDataType.NUMBER: HexSLUtilsDataType.NUMBER,
    HexDataType.STRING: HexSLUtilsDataType.STRING,
    HexDataType.DATE: HexSLUtilsDataType.DATE,
    HexDataType.TIMESTAMP_NAIVE: HexSLUtilsDataType.TIMESTAMP,
    HexDataType.TIMESTAMP_TZ: HexSLUtilsDataType.TIMESTAMPTZ,
    HexDataType.BOOLEAN: HexSLUtilsDataType.BOOLEAN,
    HexDataType.OTHER: HexSLUtilsDataType.OTHER,
    HexDataType.NULL: HexSLUtilsDataType.NULL,
}


def _datatype(type: HexDataType) -> HexSLUtilsDataType:
    return _DATATYPE_MAP[type]
