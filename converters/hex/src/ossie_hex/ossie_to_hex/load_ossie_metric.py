from ossie import OSIDataType, OSIMetric

from .context import ExportContext
from .load_ossie_datatype import load_ossie_datatype
from .load_ossie_expression import load_ossie_metric_expression


def load_ossie_metric(
    metric: OSIMetric,
    *,
    field_names: list[tuple[str, str]],
    ctx: ExportContext,
) -> OSIMetric | None:
    with ctx.problem_scope(metric.name):
        with ctx.problem_scope("expression"):
            expression = load_ossie_metric_expression(
                metric.expression, field_names=field_names, ctx=ctx
            )
        with ctx.problem_scope("datatype"):
            datatype = load_ossie_datatype(
                metric.datatype, default=OSIDataType.DECIMAL, ctx=ctx
            )

    if not expression:
        return None
    return metric.model_copy(update={"expression": expression, "datatype": datatype})
