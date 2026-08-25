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

from dataclasses import dataclass

from ossie import (
    OSIAIContext,
    OSICustomExtension,
    OSIDataset,
    OSIDataType,
    OSIDialect,
    OSIDialectExpression,
    OSIDimension,
    OSIExpression,
    OSIField,
    OSIMetric,
    OSIRelationship,
    OSISemanticModel,
)


@dataclass
class Quick:
    """Test declarations done quick™."""

    @staticmethod
    def dialect(name: str) -> OSIDialect:
        return OSIDialect(name)

    @staticmethod
    def datatype(name: str) -> OSIDataType:
        return OSIDataType(name)

    @staticmethod
    def dialect_expression(dialect: str, sql: str) -> OSIDialectExpression:
        return OSIDialectExpression(
            dialect=Quick.dialect(dialect),
            expression=sql,
        )

    @staticmethod
    def expression(dialects: list[tuple[str, str]]) -> OSIExpression:
        return OSIExpression(
            dialects=[
                Quick.dialect_expression(dialect, sql) for dialect, sql in dialects
            ],
        )

    # TODO: add datatype
    @staticmethod
    def field(
        name: str,
        datatype: str | None,
        expression: list[tuple[str, str]],
        *,
        description: str | None = None,
        label: str | None = None,
        dimension: OSIDimension | None = None,
        ai_context: OSIAIContext | None = None,
        custom_extensions: list[OSICustomExtension] | None = None,
    ) -> OSIField:
        return OSIField(
            name=name,
            datatype=Quick.datatype(datatype) if datatype else None,
            expression=Quick.expression(expression),
            dimension=dimension,
            label=label,
            description=description,
            ai_context=ai_context,
            custom_extensions=custom_extensions,
        )

    @staticmethod
    def dataset(
        name: str,
        source: str,
        fields: list[tuple[str, str, list[tuple[str, str]]]],
        *,
        description: str | None = None,
        primary_key: list[str] | None = None,
        unique_keys: list[list[str]] | None = None,
        ai_context: OSIAIContext | None = None,
        custom_extensions: list[OSICustomExtension] | None = None,
    ) -> OSIDataset:
        return OSIDataset(
            name=name,
            source=source,
            fields=[
                Quick.field(name, datatype, expression)
                for name, datatype, expression in fields
            ],
            description=description,
            primary_key=primary_key,
            unique_keys=unique_keys,
            ai_context=ai_context,
            custom_extensions=custom_extensions,
        )

    @staticmethod
    def metric(
        name: str,
        datatype: str | None,
        expression: list[tuple[str, str]],
        *,
        description: str | None = None,
        ai_context: OSIAIContext | None = None,
        custom_extensions: list[OSICustomExtension] | None = None,
    ) -> OSIMetric:
        return OSIMetric(
            name=name,
            datatype=Quick.datatype(datatype) if datatype else None,
            expression=Quick.expression(expression),
            description=description,
            ai_context=ai_context,
            custom_extensions=custom_extensions,
        )

    @staticmethod
    def relationship(
        name: str,
        from_dataset: str,
        to_dataset: str,
        from_columns: list[str],
        to_columns: list[str],
        *,
        ai_context: OSIAIContext | None = None,
        custom_extensions: list[OSICustomExtension] | None = None,
    ) -> OSIRelationship:
        return OSIRelationship(
            name=name,
            from_dataset=from_dataset,
            to=to_dataset,
            from_columns=from_columns,
            to_columns=to_columns,
            ai_context=ai_context,
            custom_extensions=custom_extensions,
        )

    @staticmethod
    def semantic_model(
        name: str,
        datasets: list[OSIDataset],
        metrics: list[OSIMetric],
        relationships: list[OSIRelationship],
        *,
        description: str | None = None,
        ai_context: OSIAIContext | None = None,
        custom_extensions: list[OSICustomExtension] | None = None,
    ) -> OSISemanticModel:
        return OSISemanticModel(
            name=name,
            datasets=datasets,
            metrics=metrics,
            relationships=relationships,
            description=description,
            ai_context=ai_context,
            custom_extensions=custom_extensions,
        )
