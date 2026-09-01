from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager

from ossie import OSIDialect

from ...hex import HexDialect, HexDialectName
from ...ossie import OssieDialectName
from ...util.context import Context
from .analysis import ExportAnalysis
from .assignment import ExportAssignment
from .hex_ids import ExportHexIds

logger = logging.getLogger(__name__)


class ExportContext(Context):
    """Context for exporting from Ossie specification to Hex specification."""

    ossie_dialect: OSIDialect
    hex_dialect: HexDialect

    _hex_ids: ExportHexIds | None
    _analysis: ExportAnalysis | None
    _assignment: ExportAssignment | None
    _unique_field_names: set[str] | None
    _dataset_name: str | None

    def __init__(self) -> None:
        super().__init__(logger=logger)
        self._hex_ids = None
        self._analysis = None
        self._assignment = None
        self._unique_field_names = None
        self._dataset_name = None

    def set_dialects(self, ossie_dialect: OSIDialect, hex_dialect: HexDialect) -> None:
        self.ossie_dialect = ossie_dialect
        self.hex_dialect = hex_dialect

    def _set_dialects(
        self, ossie_dialect: OssieDialectName, hex_dialect: HexDialectName
    ) -> None:
        """Convenience method for tests to set the dialects."""
        self.ossie_dialect = OSIDialect(ossie_dialect)
        self.hex_dialect = HexDialect(hex_dialect)

    @contextmanager
    def semantic_model_scope(self, semantic_model_name: str) -> Iterator[None]:
        """Use isolated identifiers and assignments for one semantic model."""
        self._hex_ids = ExportHexIds()
        self._analysis = ExportAnalysis()
        self._assignment = ExportAssignment()
        try:
            with self.problem_scope(semantic_model_name):
                yield
        finally:
            self._hex_ids = None
            self._analysis = None
            self._assignment = None

    def _fatal_semantic_model_scope(self) -> None:
        self.fatal(
            "Internal error", internal_message="semantic_model_scope must be active"
        )

    @property
    def hex_ids(self) -> ExportHexIds:
        if self._hex_ids is None:
            self._fatal_semantic_model_scope()
            raise ValueError("_hex_ids is not set")
        return self._hex_ids

    @property
    def analysis(self) -> ExportAnalysis:
        if self._analysis is None:
            self._fatal_semantic_model_scope()
            raise ValueError("_analysis is not set")
        return self._analysis

    @property
    def assignment(self) -> ExportAssignment:
        if self._assignment is None:
            self._fatal_semantic_model_scope()
            raise ValueError("_assignment is not set")
        return self._assignment

    @contextmanager
    def fields_scope(
        self,
        *,
        unique_field_names: set[str],
        dataset_name: str,
    ) -> Iterator[None]:
        self._unique_field_names = unique_field_names
        self._dataset_name = dataset_name
        try:
            with self.problem_scope("fields"):
                yield
        finally:
            self._unique_field_names = None
            self._dataset_name = None

    def _fatal_fields_scope(self) -> None:
        self.fatal("Internal error", internal_message="fields_scope must be active")

    @property
    def dataset_name(self) -> str | None:
        if self._dataset_name is None:
            self._fatal_fields_scope()
        return self._dataset_name

    def is_unique_field(self, field_name: str) -> bool:
        if self._unique_field_names is None:
            self._fatal_fields_scope()
            return False
        return field_name in self._unique_field_names
