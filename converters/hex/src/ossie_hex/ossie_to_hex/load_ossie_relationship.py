from ossie import OSIRelationship

from .context import ExportContext


def validate_ossie_relationship(
    ossie_relationship: OSIRelationship,
    *,
    dataset_names: set[str],
    ctx: ExportContext,
) -> bool:
    r = ossie_relationship
    valid = True
    with ctx.problem_scope(ossie_relationship.name):
        with ctx.problem_scope("from"):
            if r.from_dataset not in dataset_names:
                ctx.error(f"Could not resolve dataset name: '{r.from_dataset}'.")
                valid = False
        with ctx.problem_scope("to"):
            if r.to not in dataset_names:
                ctx.error(f"Could not resolve dataset name: '{r.to}'.")
                valid = False

        from_columns_length = len(r.from_columns)
        to_columns_length = len(r.to_columns)
        if from_columns_length != to_columns_length:
            ctx.error(
                "from_columns and to_columns must have equal length: "
                f"{from_columns_length} != {to_columns_length}"
            )
            valid = False
    return valid
