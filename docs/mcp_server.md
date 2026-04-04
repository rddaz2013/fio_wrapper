# MCP Server Integration

The FIO Wrapper includes a Model Context Protocol (MCP) server implementation, allowing it to be used as an MCP tool provider for AI assistants and other MCP clients.

## Overview

The MCP server exposes FIO functionality as a set of tools that can be called by MCP clients. This enables:

- Integration with AI assistants (Claude, ChatGPT, etc.)
- Programmatic access to FIO data through standardized protocols
- Multi-company management through MCP tools
- Real-time access to game data

## Quick Start

```python
from fio_wrapper import MCPServer, CredentialManager

# Initialize MCP server
cred_mgr = CredentialManager()
mcp_server = MCPServer(cred_mgr)

# Get available tools
tools = mcp_server.get_tools_manifest()
for tool in tools:
    print(f"Tool: {tool['name']} - {tool['description']}")

# Handle a tool call
result = mcp_server.handle_tool_call(
    tool_name="get_material",
    arguments={"ticker": "DW"}
)
print(result)
```

## Available Tools

### 1. get_material

Get information about a material by ticker.

```python
result = mcp_server.handle_tool_call("get_material", {"ticker": "DW"})
```

### 2. get_planet

Get information about a planet.

```python
result = mcp_server.handle_tool_call("get_planet", {"planet_id": "Vallis"})
```

### 3. get_exchange_data

Get commodity exchange data.

```python
result = mcp_server.handle_tool_call("get_exchange_data", {"ticker": "DW"})
```

### 4. get_company_inventory

Get inventory for a specific company.

```python
result = mcp_server.handle_tool_call("get_company_inventory", {"company_code": "COMP1"})
```

### 5. get_company_planets

Get planets owned/operated by a company.

```python
result = mcp_server.handle_tool_call("get_company_planets", {"company_code": "COMP1"})
```

### 6. get_company_ships

Get ships owned by a company.

```python
result = mcp_server.handle_tool_call("get_company_ships", {"company_code": "COMP1"})
```

### 7. add_company

Register a new company with API credentials.

```python
result = mcp_server.handle_tool_call(
    "add_company",
    {
        "company_code": "COMP1",
        "company_name": "My Company",
        "api_key": "your_api_key",
        "api_key2": "your_second_key"
    }
)
```

### 8. switch_company

Switch the active company.

```python
result = mcp_server.handle_tool_call("switch_company", {"company_code": "COMP2"})
```

### 9. list_companies

List all registered companies.

```python
result = mcp_server.handle_tool_call("list_companies", {})
```

## MCP Server Setup

### Standalone Server

Create a standalone MCP server:

```python
#!/usr/bin/env python3
from fio_wrapper import MCPServer, CredentialManager
import json
import sys

def main():
    # Initialize server
    cred_mgr = CredentialManager()
    mcp_server = MCPServer(cred_mgr)
    
    # Print tools manifest
    manifest = {"tools": mcp_server.get_tools_manifest()}
    print(json.dumps(manifest, indent=2))
    
    # Read tool calls from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line)
            tool_name = request.get("tool")
            arguments = request.get("arguments", {})
            
            result = mcp_server.handle_tool_call(tool_name, arguments)
            print(json.dumps(result))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
```

## Using with AI Assistants

### Integration Example

The MCP server enables natural language interactions with FIO data:

```
User: "What's the current price of Drinking Water?"
AI: *calls get_exchange_data tool with ticker="DW"*
AI: "Based on the exchange data, Drinking Water (DW) is currently..."
```

## Error Handling

All tool calls return results in a consistent format:

```python
# Success
{
    "result": { ... }  # Tool-specific data
}

# Error
{
    "error": "Error message"
}
```

Handle errors appropriately:

```python
result = mcp_server.handle_tool_call("get_material", {"ticker": "INVALID"})

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Result: {result['result']}")
```

## Best Practices

1. **Secure Credentials**: Never include API keys in MCP configuration - use environment variables
2. **Error Handling**: Always check for errors in tool results
3. **Rate Limiting**: Implement rate limiting for production deployments
4. **Caching**: Use FIO Wrapper's caching features to reduce API calls
5. **Monitoring**: Log tool calls for monitoring and debugging

## Use Cases

### 1. AI-Powered Trading Assistant

Enable AI to provide trading insights based on real-time market data.

### 2. Fleet Management

Track ship locations and status across multiple companies.

### 3. Inventory Tracking

Monitor inventory levels and locations in real-time.

### 4. Multi-Company Management

Compare and manage data across multiple companies seamlessly.
