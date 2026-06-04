import argparse
import sys

from mcp.server.fastmcp import FastMCP

from lib_excel.reader import (
    get_columns_with_types,
    get_sheet_count,
    get_sheet_names,
)

from .responses import (
    ColumnTypeResponse,
    SheetCountResponse,
)

DEFAULT_PORT = 5250


# ---------------------------------------------------------
# TOOL: read_sheet_names
# ---------------------------------------------------------
def read_sheet_names(path: str) -> list[str]:
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
def read_sheet_count(path: str) -> SheetCountResponse:
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
def read_columns(path: str, sheet: str, header_row: int = 0) -> list[ColumnTypeResponse]:
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


# Register the tools with the MCP server so they can be called by clients
def register_tools(server: FastMCP) -> None:
    server.tool()(read_sheet_names)
    server.tool()(read_sheet_count)
    server.tool()(read_columns)


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