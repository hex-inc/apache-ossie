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

from ossie import OSIDataset, OSIField

from .context import ExportContext
from .load_ossie_field import load_ossie_field


def load_ossie_dataset(
    dataset: OSIDataset,
    *,
    ctx: ExportContext,
) -> OSIDataset:
    """Load an Ossie dataset.

    Removes invalid fields.

    Returns an Ossie dataset with only valid fields.
    """
    with ctx.problem_scope(dataset.name):
        fields = list[OSIField]()
        with ctx.problem_scope("fields"):
            for field in dataset.fields or []:
                if field := load_ossie_field(field, ctx=ctx):
                    fields.append(field)

    return dataset.model_copy(update={"fields": fields})
