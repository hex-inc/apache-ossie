import re

_TABLE_REF_PART = r'(?:"(?:[^"]|"")+"|`[^`]+`|[A-Za-z_][A-Za-z0-9_$-]*)'
_TABLE_REF_RE = re.compile(rf"^{_TABLE_REF_PART}(?:\s*\.\s*{_TABLE_REF_PART}){{0,3}}$")


def is_table_name(value: str) -> bool:
    """Check if a value is a valid database table name.

    For example, of the form database.schema.table.
    """
    return _TABLE_REF_RE.match(value) is not None
