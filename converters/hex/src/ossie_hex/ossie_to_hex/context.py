from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager

from ossie import OSIDialect

from ..hex import HexDialect
from ..util.context import Context

logger = logging.getLogger(__name__)


class ExportContext(Context):
    """Context for exporting from Ossie specification to Hex specification."""

    def __init__(self) -> None:
        super().__init__(logger=logger)

    def set_dialects(self, ossie_dialect: OSIDialect, hex_dialect: HexDialect) -> None:
        self.ossie_dialect = ossie_dialect
        self.hex_dialect = hex_dialect

    _unique_field_names: set[str] | None = None

    @contextmanager
    def fields_scope(self, unique_field_names: set[str]) -> Iterator[None]:
        self._unique_field_names = unique_field_names
        with self.problem_scope("fields"):
            yield
        self._unique_field_names = None

    def is_unique_field(self, field_name: str) -> bool:
        if self._unique_field_names is None:
            self.fatal(
                "Internal error",
                path=[field_name],
                internal_message="fields_scope must be active",
            )
            return False
        return field_name in self._unique_field_names
