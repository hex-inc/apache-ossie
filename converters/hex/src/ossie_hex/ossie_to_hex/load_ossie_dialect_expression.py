from typing import assert_never

from ossie import OSIDialect, OSIDialectExpression

from ..util.parse_sql import ParsedExpr, SQLGlotDialect, exp, parse_one
from .context import ExportContext


def validate_ossie_field_dialect_expression(
    ossie_dialect_expression: OSIDialectExpression,
    *,
    ctx: ExportContext,
) -> bool:
    """Validate an Ossie dialect expression of an Ossie field.

    An expression is valid if it can be parsed according to its dialect.

    Returns whether the expression is valid.
    """
    parsed = parse_ossie_dialect_expression(ossie_dialect_expression, ctx=ctx)
    return parsed is not None


def validate_ossie_metric_dialect_expression(
    ossie_dialect_expression: OSIDialectExpression,
    *,
    field_names: list[tuple[str, str]],
    ctx: ExportContext,
) -> bool:
    """Validate an Ossie dialect expression of an Ossie metric.

    An expression is valid if
        - it can be parsed according to its dialect.
        - all referenced fields are in the semantic model.

    Returns whether the expression is valid.
    """
    valid = True
    parsed = parse_ossie_dialect_expression(ossie_dialect_expression, ctx=ctx)
    if not parsed:
        valid = False
    else:
        for identifier in parsed.expr.find_all(exp.Column):
            pair = (identifier.table, identifier.name)
            if pair not in field_names:
                ctx.error(
                    f"Field expression references field not in semantic model: {pair[0]}.{pair[1]}"
                )
                valid = False
    return valid


def parse_ossie_dialect_expression(
    ossie_dialect_expression: OSIDialectExpression,
    *,
    ctx: ExportContext,
) -> ParsedExpr | None:
    """Parse an Ossie dialect expression.

    Raises an exception if the expression cannot be parsed.

    Returns the parsed expression.
    """
    dialect = _to_sqlglot_dialect(ossie_dialect_expression.dialect)
    with ctx.problem_scope("expression"):
        try:
            expr = parse_one(ossie_dialect_expression.expression, read=dialect)
        except Exception as e:  # noqa: BLE001
            ctx.error(f"Unable to parse: {e}")
            return None
    return ParsedExpr(expr=expr, dialect=dialect)


def _to_sqlglot_dialect(ossie_dialect: OSIDialect) -> SQLGlotDialect | None:
    """Translate an Ossie dialect to a sqlglot dialect.

    Returns a sqlglot dialect or None (signal for sqlglot base behavior).
    """

    if ossie_dialect == OSIDialect.BIGQUERY:
        read = SQLGlotDialect.BIGQUERY
    elif ossie_dialect == OSIDialect.DATABRICKS:
        read = SQLGlotDialect.DATABRICKS
    elif ossie_dialect == OSIDialect.SNOWFLAKE:
        read = SQLGlotDialect.SNOWFLAKE
    elif ossie_dialect == OSIDialect.TABLEAU:
        read = SQLGlotDialect.TABLEAU
    elif ossie_dialect in (
        OSIDialect.ANSI_SQL,
        OSIDialect.MDX,
        OSIDialect.MAQL,
    ):
        # There's no parallel for these
        read = None
    else:
        assert_never(ossie_dialect)

    return read
