#!/usr/bin/env python3
"""Example MCP server implementation for FIO Wrapper

This example demonstrates:
- Setting up an MCP server
- Handling tool calls
- Integration with MCP clients
- Using MCP tools for multi-company management
"""

from fio_wrapper import MCPServer, CredentialManager
import json
import sys


def interactive_demo():
    """Interactive demonstration of MCP tools"""
    print("FIO Wrapper - MCP Server Example\n")
    print("=" * 50)
    
    # Initialize MCP server
    cred_mgr = CredentialManager()
    mcp_server = MCPServer(cred_mgr)
    
    # Example 1: Show available tools
    print("\n1. Available MCP Tools")
    print("-" * 50)
    
    tools = mcp_server.get_tools_manifest()
    print(f"\nTotal tools available: {len(tools)}\n")
    
    for tool in tools:
        print(f"Tool: {tool['name']}")
        print(f"  Description: {tool['description']}")
        print()
    
    # Example 2: Add a company
    print("\n2. Adding a Company via MCP")
    print("-" * 50)
    
    result = mcp_server.handle_tool_call(
        "add_company",
        {
            "company_code": "DEMO",
            "company_name": "Demo Company",
            "api_key": "demo_api_key_12345"
        }
    )
    
    print(json.dumps(result, indent=2))
    
    # Example 3: List companies
    print("\n3. Listing Companies")
    print("-" * 50)
    
    result = mcp_server.handle_tool_call("list_companies", {})
    print(json.dumps(result, indent=2))
    
    # Example 4: Get material data
    print("\n4. Getting Material Data")
    print("-" * 50)
    
    result = mcp_server.handle_tool_call(
        "get_material",
        {"ticker": "DW"}
    )
    
    if "error" in result:
        print(f"Note: {result['error']}")
        print("(This requires a valid API key)")
    else:
        print(json.dumps(result, indent=2))
    
    # Example 5: Error handling
    print("\n5. Error Handling Example")
    print("-" * 50)
    
    result = mcp_server.handle_tool_call(
        "get_company_inventory",
        {"company_code": "NONEXISTENT"}
    )
    
    if "error" in result:
        print(f"Expected error: {result['error']}")
    
    print("\n" + "=" * 50)
    print("Interactive demo completed!\n")


def stdio_server():
    """Run as a stdio MCP server (for integration with MCP clients)"""
    cred_mgr = CredentialManager()
    mcp_server = MCPServer(cred_mgr)
    
    # Print tools manifest to stdout
    manifest = {
        "version": "1.0.0",
        "tools": mcp_server.get_tools_manifest()
    }
    print(json.dumps(manifest))
    sys.stdout.flush()
    
    # Read tool calls from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            tool_name = request.get("tool")
            arguments = request.get("arguments", {})
            
            result = mcp_server.handle_tool_call(tool_name, arguments)
            print(json.dumps(result))
            sys.stdout.flush()
        
        except json.JSONDecodeError as e:
            error_response = {"error": f"Invalid JSON: {str(e)}"}
            print(json.dumps(error_response))
            sys.stdout.flush()
        
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        # Run as stdio server
        stdio_server()
    else:
        # Run interactive demo
        interactive_demo()


if __name__ == "__main__":
    main()
