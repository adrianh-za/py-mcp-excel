import argparse
import sys
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from lib_excel.reader import (
    get_columns_with_types,
    get_sheet_count,
    get_sheet_names,
    read_sheet,
)

from .responses import (
    ColumnTypeResponse,
    SheetCountResponse,
)

DEFAULT_PORT = 5250


# ---------------------------------------------------------
# TOOL: read_sheet_names
# ---------------------------------------------------------
def read_sheet_names(
    path: Annotated[str, Field(description="Path to an Excel workbook (.xlsx, .xlsm, .xls).")],
) -> list[str]:
    """
    Reads and returns the names of the sheets in the spreadsheet at the given path.

    This function takes a file path to a spreadsheet and retrieves the names of
    all the sheets contained within. It returns a list of sheet names as strings.

    :param path: The path to the spreadsheet file.
    :type path: str
    :return: A list of sheet names found in the spreadsheet.
    :rtype: list[str]
    """
    return get_sheet_names(path)


# ---------------------------------------------------------
# TOOL: read_sheet_count
# ---------------------------------------------------------
def read_sheet_count(
    path: Annotated[str, Field(description="Path to an Excel workbook (.xlsx, .xlsm, .xls).")],
) -> SheetCountResponse:
    """
    Calculate and return the sheet count of a given file.

    This function, `read_sheet_count`, receives the path to a file and determines
    the number of sheets it contains. It utilises an internal method
    `get_sheet_count` to perform the calculation and encapsulates the result in
    a `SheetCountResponse` object before returning.

    :param path: the file path to read and count sheets from
    :type path: str
    :return: the number of sheets in the file encapsulated in a
             `SheetCountResponse` object
    :rtype: SheetCountResponse
    """
    count = get_sheet_count(path)
    return SheetCountResponse(sheet_count=count)


# ---------------------------------------------------------
# TOOL: read_columns
# ---------------------------------------------------------
def read_columns(
    path: Annotated[str, Field(description="Path to an Excel workbook (.xlsx, .xlsm, .xls).")],
    sheet: Annotated[str, Field(description="Worksheet name. Use read_sheet_names to discover valid names.")],
    header_row: Annotated[int, Field(ge=0, description="Zero-based header row index.")] = 0,
) -> list[ColumnTypeResponse]:
    """
    Reads column information from a specified Excel sheet and returns a list of
    column type responses.

    This function takes the path to an Excel file, the name of the sheet, and the
    header row index to identify and process columns in the sheet. It extracts
    the column names and their types, returning them as a list of
    "ColumnTypeResponse" objects, which include the name and type of each column.

    :param path: The path to the Excel file.
    :type path: str
    :param sheet: The name of the sheet from which to read the columns.
    :type sheet: str
    :param header_row: The index of the row to be used as the header,
        which by default is the first row (index 0).
    :type header_row: int, optional
    :return: A list of "ColumnTypeResponse" objects representing the columns
        and their types.
    :rtype: list[ColumnTypeResponse]
    """
    cols = get_columns_with_types(path, sheet, header_row=header_row)
    return [ColumnTypeResponse(name=col.name, type=col.type) for col in cols]


# ---------------------------------------------------------
# TOOL: read_sheet_data
# ---------------------------------------------------------
def read_sheet_data(
    path: Annotated[str, Field(description="Path to an Excel workbook (.xlsx, .xlsm, .xls).")],
    sheet: Annotated[str, Field(description="Worksheet name. Use read_sheet_names to discover valid names.")],
    rows_to_read: Annotated[int, Field(ge=1, description="Maximum number of data rows to return.")] = 10,
    header_row: Annotated[int, Field(ge=0, description="Zero-based header row index.")] = 0,
) -> list[list[object]]:
    """
    Reads rows from a worksheet and returns them as a list of row arrays.

    :param path: The path to the Excel file.
    :type path: str
    :param sheet: The worksheet name to read.
    :type sheet: str
    :param rows_to_read: The maximum number of rows to return.
    :type rows_to_read: int
    :param header_row: The zero-based row index used as the header.
    :type header_row: int
    :return: A list of rows, where each row is a list of cell values.
    :rtype: list[list[object]]
    """
    return read_sheet(path, sheet, rows_to_read=rows_to_read, header_row=header_row)


# Register the tools with the MCP server so they can be called by clients
def register_tools(server: FastMCP) -> None:
    common_annotations = ToolAnnotations(
        title="Excel Reader",
        readOnlyHint=True,
        idempotentHint=True,
        destructiveHint=False,
        openWorldHint=False,
    )

    server.tool(
        name="excel.read_sheet_names",
        title="Read Sheet Names",
        description="Returns worksheet names in a workbook. Use this first to discover valid sheet names.",
        annotations=common_annotations,
        meta={
            "when_to_use": "Before sheet-specific tools to discover available worksheets.",
            "input_contract": "Requires a readable local workbook path.",
            "returns": "A list of worksheet names.",
        },
    )(read_sheet_names)

    server.tool(
        name="excel.read_sheet_count",
        title="Read Sheet Count",
        description="Returns the total number of worksheets in a workbook.",
        annotations=common_annotations,
        meta={
            "when_to_use": "When only workbook sheet cardinality is needed.",
            "input_contract": "Requires a readable local workbook path.",
            "returns": "A structured object with sheet_count.",
        },
    )(read_sheet_count)

    server.tool(
        name="excel.read_columns",
        title="Read Column Types",
        description="Returns column names and inferred data types for a specific worksheet.",
        annotations=common_annotations,
        meta={
            "when_to_use": "After selecting a target sheet, to inspect schema before analysis.",
            "prerequisites": ["excel.read_sheet_names"],
            "input_contract": "sheet must match an existing worksheet name; header_row is zero-based.",
            "returns": "A list of {name, type} column descriptors.",
        },
    )(read_columns)

    server.tool(
        name="excel.read_sheet_data",
        title="Read Sheet Data",
        description="Returns worksheet rows as arrays of cell values.",
        annotations=common_annotations,
        meta={
            "when_to_use": "After selecting a sheet, to preview or extract row data.",
            "prerequisites": ["excel.read_sheet_names"],
            "input_contract": "sheet must match an existing worksheet name; rows_to_read >= 1; header_row is zero-based.",
            "returns": "A list of rows, each represented as a list of cell values.",
        },
    )(read_sheet_data)


# Factory function to create and configure the MCP server with the registered tools
def create_mcp(port: int = DEFAULT_PORT) -> FastMCP:
    server = FastMCP("Excel MCP", json_response=True, port=port)
    register_tools(server)
    return server

# Create a global MCP instance that can be used when the script is run directly
mcp = create_mcp()

# Entry point for running the MCP server directly from the command line
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "streamable-http", "sse"])
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    print(f"Starting MCP with transport: {args.transport} and port: {args.port}", file=sys.stderr)

    server = mcp if args.port == DEFAULT_PORT else create_mcp(args.port)
    server.run(transport=args.transport)
