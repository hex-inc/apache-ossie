from ossie import OSIDataType

from .context import ExportContext


def load_ossie_datatype(
    ossie_datatype: OSIDataType | None,
    *,
    default: OSIDataType,
    ctx: ExportContext,
) -> OSIDataType:
    if ossie_datatype is None:
        ctx.warn(f"Missing. Hex requires a datatype. Using default '{default.value}'.")
        return default
    return ossie_datatype
