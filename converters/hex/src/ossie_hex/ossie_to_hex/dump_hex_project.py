from pathlib import Path

from ..hex import HexProject
from .context import ExportContext
from .dump_hex_resource import dump_hex_resource


def dump_hex_project(
    hex_project: HexProject,
    *,
    project_dir: Path | str,
    ctx: ExportContext,
) -> None:
    with ctx.problem_scope(hex_project.name):
        project_dir = _resolve_project_dir(project_dir)
        _write_project_dir(project_dir)

        with ctx.problem_scope("resources"):
            for hex_resource in hex_project.resources:
                dump_hex_resource(hex_resource, project_dir, ctx=ctx)


def _resolve_project_dir(project_dir: Path | str) -> Path:
    project_dir = Path(project_dir).resolve()
    return project_dir


def _write_project_dir(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
