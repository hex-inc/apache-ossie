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

from ossie import OSISemanticModel

from ..hex import HexModel
from .build_assignments import build_assignments
from .context import ExportContext
from .convert_ossie_dataset import convert_ossie_dataset
from .convert_ossie_metric import (
    analyze_ossie_metric,
    assign_ossie_metric,
    convert_ossie_metric,
)
from .convert_ossie_name import convert_ossie_name
from .convert_ossie_relationship import (
    analyze_ossie_relationship,
    assign_ossie_relationship,
    convert_ossie_relationship,
)


def convert_ossie_semantic_model(
    ossie_semantic_model: OSISemanticModel,
    *,
    ctx: ExportContext,
) -> list[HexModel]:
    """Convert an Ossie semantic model to Hex models.

    Returns the converted Hex models.
    """
    with ctx.semantic_model_scope(ossie_semantic_model.name):
        _store_converted_names(ossie_semantic_model, ctx=ctx)

        with ctx.problem_scope("datasets"):
            for ossie_dataset in ossie_semantic_model.datasets:
                if hex_model := convert_ossie_dataset(ossie_dataset, ctx=ctx):
                    ctx.assignment.add_model(ossie_dataset.name, hex_model)

        with ctx.problem_scope("metrics"):
            for ossie_metric in ossie_semantic_model.metrics or []:
                analysis = analyze_ossie_metric(ossie_metric, ctx=ctx)
                ctx.analysis.set_for_metric(analysis)

        with ctx.problem_scope("relationships"):
            for ossie_relationship in ossie_semantic_model.relationships or []:
                analysis = analyze_ossie_relationship(ossie_relationship, ctx=ctx)
                ctx.analysis.set_for_relationship(analysis)

        build_assignments(ctx=ctx)

        with ctx.problem_scope("metrics"):
            for ossie_metric in ossie_semantic_model.metrics or []:
                if result := convert_ossie_metric(ossie_metric, ctx=ctx):
                    assign_ossie_metric(ossie_metric, result, ctx=ctx)

        with ctx.problem_scope("relationships"):
            for ossie_relationship in ossie_semantic_model.relationships or []:
                if result := convert_ossie_relationship(ossie_relationship, ctx=ctx):
                    assign_ossie_relationship(ossie_relationship, result, ctx=ctx)

        hex_models = ctx.assignment.models()

    return hex_models


def _store_converted_names(
    ossie_semantic_model: OSISemanticModel,
    *,
    ctx: ExportContext,
) -> None:
    for d in ossie_semantic_model.datasets:
        with ctx.problem_scope("datasets", d.name):
            if id := convert_ossie_name(d.name, ctx=ctx):
                ctx.hex_ids.set_for_dataset(d.name, id)
        for f in d.fields or []:
            with ctx.problem_scope("datasets", d.name, "fields", f.name):
                if id := convert_ossie_name(f.name, ctx=ctx):
                    ctx.hex_ids.set_for_field(d.name, f.name, id)
    for m in ossie_semantic_model.metrics or []:
        with ctx.problem_scope("metrics", m.name):
            if id := convert_ossie_name(m.name, ctx=ctx):
                ctx.hex_ids.set_for_metric(m.name, id)
    for r in ossie_semantic_model.relationships or []:
        with ctx.problem_scope("relationships", r.name):
            if id := convert_ossie_name(r.name, ctx=ctx):
                ctx.hex_ids.set_for_relationship(r.name, id)
