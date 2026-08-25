from dataclasses import dataclass

from hex_sl_utils._vendor.sqlglot import Dialects as SQLGlotDialect
from hex_sl_utils._vendor.sqlglot import exp, parse_one


@dataclass
class ParsedExpr:
    expr: exp.Expression
    dialect: SQLGlotDialect | None


__all__ = [
    "ParsedExpr",
    "SQLGlotDialect",
    "exp",
    "parse_one",
]
