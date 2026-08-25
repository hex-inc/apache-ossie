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

from ..util.rewrite_refs import hex_refs_to_ossie
from ..util.rewrite_refs import qualify_hex_ref as qualify_ref
from .context import ConvertHexCtx


def rewrite_hex_refs(sql: str, *, ctx: ConvertHexCtx) -> str:
    """Rewrite SQL expressions containing Hex semantic references to Ossie semantic references."""
    return hex_refs_to_ossie(sql, model=ctx.model_id)


def qualify_hex_ref(reference: str, *, ctx: ConvertHexCtx) -> str:
    """Qualify a standalone Hex semantic reference."""
    return qualify_ref(reference, model=ctx.model_id)
