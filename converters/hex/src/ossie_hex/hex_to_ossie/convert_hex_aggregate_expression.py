from ossie import OssieDialectExpression, OssieExpression

from ..hex import HexAggregateExpression
from .context import ImportContext


def convert_hex_aggregate_expression(
    hex_aggregate_expression: HexAggregateExpression,
    *,
    ctx: ImportContext,
) -> OssieExpression | None:
    if hex_aggregate_expression.func:
        # TODO: using hex-sl-utils, compile func..of..filters to a SQL expression.
        sql_expression = str(hex_aggregate_expression.func)
    elif hex_aggregate_expression.func_sql:
        with ctx.problem_scope("func_sql"):
            # TODO: using hex-sl-utils and Dialect class, convert sql expression with
            # maybe hex interpolation to a SQL expression.
            sql_expression = hex_aggregate_expression.func_sql
    elif hex_aggregate_expression.func_calc:
        with ctx.problem_scope("func_calc"):
            # TODO: using hex-sl-utils and Dialect class, convert hex calc expression
            # with maybe hex interpolation to a SQL expression.
            sql_expression = hex_aggregate_expression.func_calc
    else:
        ctx.fatal(
            "Unexpected aggregate expression shape.",
            internal_message="Should have been validated in the load phase to be one of func, func_sql, or func_calc",
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
