from ossie import OssieDialectExpression, OssieExpression

from ..hex import HexScalarExpression
from .context import ImportContext


def convert_hex_scalar_expression(
    hex_scalar_expression: HexScalarExpression,
    *,
    ctx: ImportContext,
) -> OssieExpression | None:
    if hex_scalar_expression.expr_sql:
        with ctx.problem_scope("expr_sql"):
            # TODO: using hex-sl-utils and Dialect class, convert sql expression with
            # maybe hex interpolation to a SQL expression.
            sql_expression = hex_scalar_expression.expr_sql
    elif hex_scalar_expression.expr_calc:
        with ctx.problem_scope("expr_calc"):
            # TODO: using hex-sl-utils and Dialect class, convert the hex calc expression to a SQL
            sql_expression = hex_scalar_expression.expr_calc
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
