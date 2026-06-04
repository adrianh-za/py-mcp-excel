from fastapi import APIRouter, FastAPI, HTTPException

from lib_excel.reader import (
    get_columns_with_types,
    get_sheet_count,
    get_sheet_names,
)

from .responses import (
    ColumnTypeResponse,
    SheetCountResponse,
)

# Expose OpenAPI and Swagger UI under the /api prefix
app = FastAPI(
    title="Excel API",
    description="A simple Excel API",
    version="1.0.0",
    openapi_url="/api/excel/openapi.json",
    docs_url="/api/excel/swagger",
    redoc_url="/api/excel/openapi",
)

# Use a router to group API endpoints under /api
api_router = APIRouter(prefix="/api/excel")


@api_router.get("/sheet-names", summary="Get sheet names", tags=["Reader"])
async def read_sheet_names(path: str) -> list[str]:
    try:
        return get_sheet_names(path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get("/sheet-count", summary="Get sheet count", tags=["Reader"])
async def read_sheet_count(path: str) -> SheetCountResponse:
    try:
        count = get_sheet_count(path)
        return SheetCountResponse(sheet_count=count)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get("/columns", summary="Get sheet columns", tags=["Reader"])
async def read_columns(path: str, sheet: str, header_row: int = 0) -> list[ColumnTypeResponse]:
    try:
        cols = get_columns_with_types(path, sheet, header_row=header_row)
        return [ColumnTypeResponse(name=col.name, type=col.type) for col in cols]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Include the router
app.include_router(api_router)