from typing import Annotated

HexSql = Annotated[
    str,
    """A SQL expression in the context of a Hex entity.

    Possibly contains Hex semantic references. 
    
    Dimension `expr_sql` examples:
        - local logical, unqualified: `${dimension}`
        - foreign logical, qualified: `${relation.dimension}`
        - foreign physical, qualified: `${relation}.column`

    Measure `func_sql` examples:
        - local logical, unqualified: `${dimension}` or `${measure}`
        - foreign logical, qualified: `${relation.dimension}` or `${relation.measure}`
        - foreign physical, qualified: `${relation}.column`
    """,
]
