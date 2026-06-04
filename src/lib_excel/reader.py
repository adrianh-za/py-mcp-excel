from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class ColumnType:
    name: str
    type: str


def get_sheet_names(path: str) -> list[str]:
    with pd.ExcelFile(path) as xls:
        return [str(name) for name in xls.sheet_names]


def get_sheet_count(path: str) -> int:
    return len(get_sheet_names(path))


def get_columns(path: str, sheet: str, header_row: int = 0) -> list[str]:
    df = pd.read_excel(path, sheet_name=sheet, nrows=0, header=header_row)  # pyright: ignore[reportUnknownMemberType]
    return [str(column) for column in df.columns]


def get_columns_with_types(path: str, sheet: str, header_row: int = 0) -> list[ColumnType]:
    df = pd.read_excel(path, sheet_name=sheet, header=header_row)  # pyright: ignore[reportUnknownMemberType]
    return [ColumnType(name=str(column), type=str(dtype)) for column, dtype in df.dtypes.items()]
