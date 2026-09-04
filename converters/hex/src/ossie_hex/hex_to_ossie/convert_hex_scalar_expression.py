from ossie import OssieExpression

from ..hex import HexScalarExpression
from .context import ImportContext


def convert_hex_scalar_expression(
    hex_scalar_expression: HexScalarExpression,
    *,
    ctx: ImportContext,
) -> OssieExpression | None:
    # TODO
    pass
