from os import getcwd
from pathlib import Path

from ossie import OssieDocument

from ossie_hex.util.yaml import dump_yaml

from .context import ImportContext


def dump_ossie_document(
    ossie_document: OssieDocument,
    *,
    path: Path | str | None = None,
    ctx: ImportContext,
) -> Path | None:
    """Dump an Ossie document to a file."""
    path = _resolve_file(path, ctx=ctx)
    json_data = _serialize_to_json(ossie_document, ctx=ctx)
    yml_data = _serialize_to_yaml(json_data, ctx=ctx)
    path = _write_file(path, yml_data, ctx=ctx)
    return path


def _resolve_file(path: Path | str, *, ctx: ImportContext) -> Path | None:
    try:
        path = Path(path).resolve()
    except (OSError, ValueError) as e:
        ctx.error(f"Failed to resolve file path: {e}")
        return None
    if not path.is_relative_to(getcwd()):
        ctx.error(f"File path would write files outside the output directory: {path}")
        return None
    return path


def _serialize_to_json(
    ossie_document: OssieDocument, *, ctx: ImportContext
) -> dict | None:
    json_data = ossie_document.model_dump(by_alias=True, exclude_none=True, mode="json")
    return json_data


def _serialize_to_yaml(json_data: dict | None, *, ctx: ImportContext) -> str | None:
    if json_data is None:
        return None
    yml_data = dump_yaml(json_data)
    return yml_data


def _write_file(
    path: Path | None, data: str | None, *, ctx: ImportContext
) -> Path | None:
    if path is None or data is None:
        return None
    try:
        path.write_text(data, encoding="utf-8")
    except (OSError, ValueError) as e:
        ctx.error(f"Failed to write file: {e}")
        return None
    return path
