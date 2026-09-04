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

from collections.abc import Mapping
from typing import Literal

ImportProblemCode = Literal[
    "hex-name",
    "hex-datatype-number",
]
"""Codes for problems reported while converting Hex to Ossie."""

IMPORT_PROBLEM_SUMMARIES: Mapping[ImportProblemCode, str] = {
    "hex-name": "Display names are not supported in Ossie and are dropped.",
    "hex-datatype-number": "The Hex Number datatype is narrowed to the Ossie Decimal datatype (not Float or Integer).",
}
