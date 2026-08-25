# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager

from ossie import OSIDialect

from ..hex_types import HexModel, HexRelation
from ..util.errors import ConversionWarning


class ConvertHexCtx:
    """State shared throughout Hex-to-Ossie conversion."""

    def __init__(self, *, ossie_dialect: OSIDialect) -> None:
        self.ossie_dialect = ossie_dialect
        self.warnings: list[ConversionWarning] = []
        self._dimension_ids_by_model: dict[str, set[str]] = {}
        self._metric_names: set[str] = set()
        self._model: HexModel | None = None
        self._relation_targets_by_id: dict[str, str] = {}

    @property
    def model(self) -> HexModel:
        if self._model is None:
            raise ValueError("No model scope is active")
        return self._model

    @property
    def model_id(self) -> str:
        return self.model.id

    @property
    def relation_targets_by_id(self) -> Mapping[str, str]:
        return self._relation_targets_by_id

    @property
    def dimension_ids_by_model(self) -> Mapping[str, set[str]]:
        return self._dimension_ids_by_model

    @contextmanager
    def model_scope(self, model: HexModel) -> Iterator[None]:
        """Make the given model current."""
        if self._model is not None:
            raise RuntimeError("A model scope is already active")
        self._model = model
        self._relation_targets_by_id = {}
        try:
            yield
        finally:
            self._model = None
            self._relation_targets_by_id = {}

    def warn(self, message: str) -> None:
        self.warnings.append(ConversionWarning(message))

    def register_dimensions(self, model: HexModel) -> None:
        """Index a model's declared dimensions for project-wide resolution."""
        self._dimension_ids_by_model[model.id] = {
            dimension.id for dimension in model.dimensions
        }

    def register_relation(self, relation: HexRelation) -> None:
        """Index a relation that was successfully converted to Ossie."""
        self._relation_targets_by_id[relation.id] = relation.target

    def claim_metric_name(self, measure_id: str) -> str:
        """Claim a document-wide metric name, qualifying collisions by model."""
        metric_name = measure_id
        if metric_name in self._metric_names:
            # Name the Ossie metric for a measure whose ID another model already took.
            # Hex measure IDs are unique within their model, Ossie metric names within
            # the whole document, so a measure ID that two models share has to be
            # qualified. There is no inverse anywhere in the export: a name of this shape
            # is only known to be qualified because the payload recorded the ID it was
            # built from -- anyone may author an Ossie metric called ``orders__revenue``
            # and mean it literally.
            metric_name = f"{self.model_id}__{measure_id}"
        self._metric_names.add(metric_name)
        return metric_name
