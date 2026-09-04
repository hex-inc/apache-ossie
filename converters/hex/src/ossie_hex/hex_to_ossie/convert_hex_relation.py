from ossie import OssieRelationship

from ..hex import HexRelation
from .context import ImportContext


def convert_hex_relation(
    hex_relation: HexRelation,
    *,
    ctx: ImportContext,
) -> OssieRelationship | None:
    # TODO
    pass
