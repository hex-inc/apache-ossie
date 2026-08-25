from pathlib import Path

from pydantic_core import PydanticSerializationError
from yaml import YAMLError

from ..hex import HexResource
from ..util.yaml import dump_yaml
from .context import ExportContext


def dump_hex_resource(
    hex_resource: HexResource,
    project_dir: Path,
    *,
    ctx: ExportContext,
) -> None:
    """Serialize and write a Hex resource to a file.

    Args:
        - `hex_resource`: A Hex resource
        - `project_dir`: A canonical path to the directory for the Hex project
    """
    with ctx.problem_scope(hex_resource.id):
        file_path = _resolve_file_path(project_dir, hex_resource, ctx=ctx)
        json_data = _serialize_to_json(hex_resource, ctx=ctx)
        yaml_data = _serialize_to_yaml(json_data, ctx=ctx)
        _write_file(file_path, yaml_data, ctx=ctx)


def _serialize_to_json(hex_resource: HexResource, *, ctx: ExportContext) -> dict | None:
    try:
        return hex_resource.model_dump(
            mode="json",
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )
    except PydanticSerializationError as e:
        ctx.error(f"Failed to serialize to JSON: {e}")


def _serialize_to_yaml(json_data: dict | None, *, ctx: ExportContext) -> str | None:
    if json_data is None:
        return None
    try:
        return dump_yaml(json_data)
    except YAMLError as e:
        ctx.error(f"Failed to serialize to YAML: {e}")


def _resolve_file_path(
    project_dir: Path, hex_resource: HexResource, *, ctx: ExportContext
) -> Path | None:
    try:
        file_path = (project_dir / f"{hex_resource.id}.yml").resolve()
    except (OSError, ValueError) as e:
        ctx.error(f"Failed to resolve file path: {e}")
        return None
    if not file_path.is_relative_to(project_dir):
        ctx.error("Resource id would write a file outside the project directory")
        return None
    return file_path


def _write_file(
    file_path: Path | None,
    data: str | None,
    *,
    ctx: ExportContext,
) -> None:
    if file_path is None or data is None:
        return
    try:
        file_path.write_text(data, encoding="utf-8")
    except OSError as e:
        ctx.error(f"Failed to write to file: {e}")
