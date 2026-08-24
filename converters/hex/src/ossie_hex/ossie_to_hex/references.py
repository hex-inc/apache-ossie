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

import re


def references(expr: str, dataset_name: str) -> bool:
    """Whether ``expr`` qualifies anything with ``dataset_name``."""

    # Textual rather than parsed, so it only recognizes the ``name.`` qualifier
    # form and would also see one inside a string literal. The word boundary
    # stops ``orders`` from matching ``back_orders.total``.
    return bool(re.search(rf"\b{re.escape(dataset_name)}\.", expr))
