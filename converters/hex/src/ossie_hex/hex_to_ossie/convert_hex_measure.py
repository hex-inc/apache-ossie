from ossie import OssieMetric

from ..hex import HexMeasure
from .context import ImportContext
from .convert_hex_aggregate_expression import convert_hex_aggregate_expression
from .convert_hex_datatype import convert_hex_datatype


def convert_hex_measure(
    hex_measure: HexMeasure,
    *,
    ctx: ImportContext,
) -> OssieMetric | None:
    m_name = hex_measure.id

    with ctx.problem_scope("name"):
        ctx.warn("Not supported", code="hex-name")

    m_description = hex_measure.description or None

    with ctx.problem_scope("type"):
        m_datatype = convert_hex_datatype(hex_measure.type, ctx=ctx)

    with ctx.problem_scope("visibility"):
        ctx.warn("Not supported", code="hex-visibility")

    m_expression = convert_hex_aggregate_expression(hex_measure, ctx=ctx)

    with ctx.problem_scope("semi_additive"):
        ctx.warn("Not supported", code="hex-semi-additive")

    if m_expression is None:
        return None

    return OssieMetric(
        name=m_name,
        expression=m_expression,
        description=m_description,
        datatype=m_datatype,
        # attributes not set:
        # - ai_context: Hex does not encode this concept
        # - custom_extensions: Hex does not support this concept
    )
