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

from ossie import OssieDataset, OssieField, OssieMetric, OssieRelationship

from ..hex import HexModel
from .context import ImportContext
from .convert_hex_dimension import convert_hex_dimension
from .convert_hex_measure import convert_hex_measure
from .convert_hex_relation import convert_hex_relation


def convert_hex_model(
    hex_model: HexModel,
    *,
    ctx: ImportContext,
) -> tuple[OssieDataset, list[OssieMetric], list[OssieRelationship]] | None:
    with ctx.problem_scope(hex_model.id):
        d_name = hex_model.id
        d_description = hex_model.description or None

        with ctx.problem_scope("name"):
            ctx.warn("Not supported", code="hex-name")

        with ctx.problem_scope("source"):
            if hex_model.base_sql_query is not None:
                d_source = hex_model.base_sql_query
            elif hex_model.base_sql_table is not None:
                d_source = hex_model.base_sql_table
            else:
                # load phase should prevent this case
                d_source = None

        d_unique_keys = list[str]()
        d_fields = list[OssieField]()
        for h_dimension in hex_model.dimensions:
            if h_dimension.unique:
                d_unique_keys.append(h_dimension.name)
            if ossie_field := convert_hex_dimension(h_dimension, ctx=ctx):
                d_fields.append(ossie_field)

        ossie_metrics = list[OssieMetric]()
        for h_measure in hex_model.measures:
            if ossie_metric := convert_hex_measure(h_measure, ctx=ctx):
                ossie_metrics.append(ossie_metric)

        ossie_relationships = list[OssieRelationship]()
        for h_relation in hex_model.relations:
            if ossie_relationship := convert_hex_relation(h_relation, ctx=ctx):
                ossie_relationships.append(ossie_relationship)

        if d_source is None:
            return None

        ossie_dataset = OssieDataset(
            name=d_name,
            description=d_description,
            source=d_source,
            unique_keys=d_unique_keys,
            fields=d_fields,
            # attributes not set:
            # - primary_key: Hex does not encode this concept
            # - ai_context: Hex does not encode this concept
            # - custom_extensions: Hex does not support this concept
        )

        return ossie_dataset, ossie_metrics, ossie_relationships
