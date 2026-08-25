from ossie import OSIDataType, OSIField

from .context import ExportContext
from .load_ossie_datatype import load_ossie_datatype
from .load_ossie_expression import load_ossie_field_expression


def load_ossie_field(
    field: OSIField,
    *,
    ctx: ExportContext,
) -> OSIField | None:
    with ctx.problem_scope(field.name):
        with ctx.problem_scope("expression"):
            expression = load_ossie_field_expression(field.expression, ctx=ctx)
        with ctx.problem_scope("datatype"):
            datatype = load_ossie_datatype(
                field.datatype, default=OSIDataType.STRING, ctx=ctx
            )

    if expression is None:
        return None
    return field.model_copy(update={"expression": expression, "datatype": datatype})
