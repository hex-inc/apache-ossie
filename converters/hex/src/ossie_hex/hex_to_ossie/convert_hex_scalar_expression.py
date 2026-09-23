from collections.abc import Mapping
from typing import TypeAlias

from hex_sl_utils.calc import parse_calc_expression
from hex_sl_utils.datatype.datatype import DataType as HexSLUtilsDataType
from hex_sl_utils.expr import (
    ExpressionContext,
    ExpressionKind,
    TypedSelectExpression,
    rewrite_placeholder_references,
)
from hex_sl_utils.expr.expr_references import ResolveReference
from ossie import OssieDialectExpression, OssieExpression

from ossie_hex.util.parse_sql import exp

from ..hex import HexDataType, HexScalarExpression
from .context import ImportContext


def convert_hex_scalar_expression(
    hex_scalar_expression: HexScalarExpression,
    *,
    ctx: ImportContext,
) -> OssieExpression | None:
    if hex_scalar_expression.expr_sql:
        with ctx.problem_scope("expr_sql"):
            sql_expression = _compile_expr_sql(
                hex_scalar_expression.expr_sql,
                ctx=ctx,
            )
    elif hex_scalar_expression.expr_calc:
        with ctx.problem_scope("expr_calc"):
            sql_expression = _compile_expr_calc(
                hex_scalar_expression.expr_calc,
                ctx=ctx,
            )
    else:
        ctx.fatal(
            "Unexpected scalar expression shape.",
            internal_message="Should have been validated in the load phase to be one of expr_sql or expr_calc",
        )
        return None
    ossie_dialect_expression = OssieDialectExpression(
        dialect=ctx.ossie_dialect,
        expression=sql_expression,
    )
    ossie_expression = OssieExpression(
        dialects=[ossie_dialect_expression],
    )
    return ossie_expression


# TODO: unclear whether the spec actually allows logical references (local or foreign) in field expressions


def _compile_expr_sql(
    expr_sql: str,
    *,
    ctx: ImportContext,
) -> str:
    """Compile a SQL column expression that may contain Hex semantic placeholders
    to an underlying SQL dialect expression.

    Args:
        expr_sql: a SQL column expression that may contain Hex semantic placeholders
        ctx: the import context

    Returns:
        a SQL string in the project dialect
    """
    resolve = _build_resolve_reference(ctx=ctx)
    result = rewrite_placeholder_references(
        expr_sql,
        resource=ctx.model.id,
        dialect=ctx.hex_dialect,
        resolve=resolve,
    )
    if result.unresolved_references:
        ctx.warn(
            f"Unresolved references: {result.unresolved_references}",
            code="hex-unresolved-references",
        )
    return result.sql


def _compile_expr_calc(
    expr_calc: str,
    *,
    ctx: ImportContext,
) -> str:
    """Compile a Hex calculation formula expression to an underlying SQL dialect expression.

    Args:
        expr_calc: a Hex calculation formula expression
        ctx: the import context

    Returns:
        a SQL string in the project dialect
    """
    calc = parse_calc_expression(expr_calc)
    columns = _build_columns(ctx=ctx)
    substitutions = _build_substitutions(ctx=ctx)
    typed_expr = ctx.hex_dialect.compile_calc_expr(
        expr=calc,
        context=ExpressionContext.PROJECTION,
        columns=columns,
        substitutions=substitutions,
        timezone="UTC",
        parameters={},  # Disallow jinja templating
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
    # only dimensions are in scope for scalar expressions
    m = ctx.model
    columns: _Columns = {d.id: _datatype(d.type) for d in m.dimensions}
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
    return substitutions


def _build_resolve_reference(*, ctx: ImportContext) -> ResolveReference:
    m = ctx.model
    p = ctx.project
    pairs: dict[tuple[str, str], tuple[str, str]] = {}
    for d in m.dimensions:
        pairs[(m.id, d.id)] = (m.id, d.id)
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
