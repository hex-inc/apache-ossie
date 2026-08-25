from ossie import OSIDialectExpression, OSIExpression

from .context import ExportContext
from .load_ossie_dialect_expression import (
    validate_ossie_field_dialect_expression,
    validate_ossie_metric_dialect_expression,
)


def load_ossie_field_expression(
    ossie_expression: OSIExpression,
    *,
    ctx: ExportContext,
) -> OSIExpression | None:
    """Load an Ossie expression declared on an Ossie field.

    An expression is valid if it contains at least one valid Ossie dialect expression.

    Returns an Ossie expression with only valid dialects, or None if the expression is invalid.
    """
    # ASSUMPTION: Ossie field expressions are only allowed to reference underlying
    # physical columns (on database table/view/query) and do not contain logical
    # field references (Ossie FieldExpr of any shape). So we do nothing to validate
    # the parsed output of the dialect expression(s).
    result: OSIExpression | None = None
    with ctx.problem_scope("dialects"):
        dialects = list[OSIDialectExpression]()
        for entry in ossie_expression.dialects:
            with ctx.problem_scope(entry.dialect.value):
                valid = validate_ossie_field_dialect_expression(entry, ctx=ctx)
                if valid:
                    dialects.append(entry)
        result = OSIExpression(dialects=dialects)
        if not result.dialects:
            ctx.error("Expression must have at least one valid dialect")
            result = None
    return result


def load_ossie_metric_expression(
    expression: OSIExpression,
    *,
    field_names: list[tuple[str, str]],
    ctx: ExportContext,
) -> OSIExpression | None:
    """Load an Ossie expression declared on an Ossie metric.

    Args:
      - `field_names`: reachable (dataset, field) name pairs in the semantic model.

    An expression is valid if it contains at least one valid Ossie dialect expression.

    Returns an Ossie expression with only valid dialects, or None if the expression is invalid.
    """
    result: OSIExpression | None = None
    with ctx.problem_scope("dialects"):
        dialects = list[OSIDialectExpression]()
        for entry in expression.dialects:
            with ctx.problem_scope(entry.dialect.value):
                valid = validate_ossie_metric_dialect_expression(
                    entry, field_names=field_names, ctx=ctx
                )
                if valid:
                    dialects.append(entry)
        result = OSIExpression(dialects=dialects)
        if not result.dialects:
            ctx.error("Expression must have at least one valid dialect")
            result = None
    return result
