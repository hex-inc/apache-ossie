from ossie import OssieMetric

from ..hex import HexMeasure
from .context import ImportContext


def convert_hex_measure(
    hex_measure: HexMeasure,
    *,
    ctx: ImportContext,
) -> OssieMetric | None:
    # TODO
    pass
