from ._brand import HexDataType

_TEMPORAL_TYPES = frozenset(
    [
        HexDataType.DATE,
        HexDataType.TIMESTAMP_NAIVE,
        HexDataType.TIMESTAMP_TZ,
    ]
)


def is_temporal_hex_datatype(value: HexDataType) -> bool:
    return value in _TEMPORAL_TYPES
