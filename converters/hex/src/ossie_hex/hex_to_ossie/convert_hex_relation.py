from ossie import OssieRelationship

from ..hex import HexRelation
from .context import ImportContext


def convert_hex_relation(
    hex_relation: HexRelation,
    *,
    ctx: ImportContext,
) -> OssieRelationship | None:
    with ctx.problem_scope(hex_relation.id):
        r_name = hex_relation.id

    with ctx.problem_scope("visibility"):
        ctx.warn("Not supported", code="hex-visibility")

    # TODO:
    # - if `type` is many-to-one or one-to-one, then base model is `from_dataset` and target model is `to_dataset`.
    # - if `type` is one-to-many, then base model is `to_dataset` and target model is `from_dataset`.
    # - if `type` is one-to-one, warn that fidelity will be lost and is implicitly many-to-one in Ossie.
    # - parse `join_sql`
    #   - If only uses `${ }` interpolation for dimension references, then cannot be converted
    #   - Otherwise, columns off of the target become target (respective to/from) columns, and other columns
    #     are base (respective from/to) columns.

    r_from_dataset = ""  # TODO
    r_to_dataset = ""  # TODO
    r_from_columns = []  # TODO
    r_to_columns = []  # TODO

    return OssieRelationship(
        name=r_name,
        from_dataset=r_from_dataset,
        to=r_to_dataset,
        from_columns=r_from_columns,
        to_columns=r_to_columns,
    )
