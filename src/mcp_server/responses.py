from pydantic import BaseModel


class SheetCountResponse(BaseModel):
    sheet_count: int


class ColumnTypeResponse(BaseModel):
    name: str
    type: str
