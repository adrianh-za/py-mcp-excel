# Excel MCP and FastAPI Server

A Python project that exposes Excel file information via the Model Context Protocol (MCP) and a FastAPI REST API. It allows reading Excel spreadsheets to extract sheet names, sheet counts, and column information with data types.
The point of the API is for easier testing, while the MCP server is the main focus for integration with MCP-compatible tools and agents.

## Features

- **MCP Server**: Model Context Protocol server with tools for Excel file inspection
- **REST API**: FastAPI-based HTTP endpoints for programmatic access
- **Excel Reader Library**: Core functionality for reading Excel files using pandas and openpyxl

### Available Tools & Endpoints

| Function | MCP Tool | API Endpoint | Description |
|----------|----------|---------------|-------------|
| Get sheet names | `read_sheet_names(path)` | `GET /api/excel/sheet-names?path={path}` | Returns list of sheet names in an Excel file |
| Get sheet count | `read_sheet_count(path)` | `GET /api/excel/sheet-count?path={path}` | Returns the number of sheets in an Excel file |
| Get columns with types | `read_columns(path, sheet, header_row=0)` | `GET /api/excel/columns?path={path}&sheet={sheet}&header_row={header_row}` | Returns column names and their data types from a specific sheet |

## Prerequisites

- Python 3.14+
- pip or uv for package management

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/adrianh-za/py-mcp-excel.git
cd py-mcp-excel

# Install dependencies using pip
pip install -e .

# Or using uv
uv pip install -e .
```

### Dependencies

- `fastapi` - Web framework for the REST API
- `mcp` - Model Context Protocol Python SDK
- `openpyxl` - Excel file reading
- `pandas` - Data manipulation and Excel parsing
- `uvicorn` - ASGI server for FastAPI

## Running the Project

### REST API Server

Start the FastAPI server:

```bash
PYTHONPATH=src python -m api_server.endpoints
```

The API will be available at:
- **Swagger UI**: `http://localhost:8000/api/excel/swagger`
- **OpenAPI JSON**: `http://localhost:8000/api/excel/openapi.json`
- **ReDoc**: `http://localhost:8000/api/excel/openapi`

**Note**: You can customize the server using standard Uvicorn arguments:

```bash
PYTHONPATH=src uvicorn api_server.endpoints:app --host 127.0.0.1 --port 8000 --reload
```

### MCP Server

Start the MCP server with your preferred transport:

```bash
PYTHONPATH=src python -m mcp_server.tools
```

**Optional Arguments:**
- `--transport`: `stdio` (default) | `sse` | `streamable-http`
- `--port`: `5250` (default)

Examples:
```bash
# STDIO transport (default)
PYTHONPATH=src npx @modelcontextprotocol/inspector python -m mcp_server.tools

# Streamable HTTP transport
PYTHONPATH=src python -m mcp_server.tools --transport streamable-http --port 5250

# Server-Sent Events transport
PYTHONPATH=src python -m mcp_server.tools --transport sse --port 5250
```

## MCP Inspector Configuration

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to test and interact with the MCP server.

### Install and Run Inspector

```bash
npx @modelcontextprotocol/inspector
```

### Configuration for Streamable HTTP

- **Transport Type**: `Streamable HTTP`
- **URL**: `http://localhost:5250/mcp`
- **Connection Type**: `Via Proxy`
- **Authentication**: No custom headers or tokens required

### Configuration for STDIO

- **Transport Type**: `STDIO`
- **Command**: `python`
- **Arguments**: `-m mcp_server.tools` (with `PYTHONPATH=src` set in environment)
- **Authentication**: No custom headers or tokens required

### Configuration for SSE

- **Transport Type**: `Server-Sent Events`
- **URL**: `http://localhost:5250/sse`
- **Authentication**: No custom headers or tokens required

## API Usage Examples

### cURL Examples

```bash
# Get sheet names from an Excel file
curl "http://localhost:8000/api/excel/sheet-names?path=/path/to/file.xlsx"

# Get sheet count
curl "http://localhost:8000/api/excel/sheet-count?path=/path/to/file.xlsx"

# Get columns with types from a specific sheet
curl "http://localhost:8000/api/excel/columns?path=/path/to/file.xlsx&sheet=Sheet1"

# Get columns with custom header row
curl "http://localhost:8000/api/excel/columns?path=/path/to/file.xlsx&sheet=Sheet1&header_row=2"
```