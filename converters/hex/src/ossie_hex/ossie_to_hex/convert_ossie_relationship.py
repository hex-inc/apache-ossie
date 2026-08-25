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

from ossie import OSIRelationship

from .context import ExportContext
from .convert_ossie_name import convert_ossie_name


def convert_ossie_relationship(
    ossie_relationship: OSIRelationship,
    *,
    ctx: ExportContext,
) -> None:
    with ctx.problem_scope(ossie_relationship.name):
        # TODO: `convert_ossie_dataset` will already do `name` conversion, so it
        # should probably be lifted to a shared store.
        with ctx.problem_scope("name"):
            hex_relation_id = convert_ossie_name(ossie_relationship.name, ctx=ctx)
            if hex_relation_id is None:
                return

        with ctx.problem_scope("ai_context"):
            if ossie_relationship.ai_context is not None:
                ctx.warn("Not supported")

        with ctx.problem_scope("custom_extensions"):
            if ossie_relationship.custom_extensions is not None:
                ctx.warn("Not supported")

        # Attributes not set:
        # - HexRelation.visibility: Ossie does not support this concept

        # TODO: return some partial conversion shape
        return


# ASSUMPTION: it's kind of ambiguous whether the spec is defining "columns" as
# physical or logical columns (i.e. a column on the underlying table/view/query
# or a field on the respective dataset). For now, we assume a physical column.
# In the case that it can be a logical column, we would need to resolve each
# value to the corresponding HexDimension id and wrap in Hex semantic reference
# syntax (${}) like the relation_id
