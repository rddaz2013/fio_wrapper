"""MCP (Model Context Protocol) Server for FIO Wrapper

This module implements an MCP server that provides tools for accessing
FIO/FNAR API data through the Model Context Protocol.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from fio_wrapper.fio import FIO
from fio_wrapper.multi_company import MultiCompanyFIO
from fio_wrapper.credentials import CredentialManager

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP Server for FIO Wrapper
    
    This server exposes FIO functionality through MCP-compatible tools.
    It supports:
    - Multi-company management
    - Material lookups
    - Planet information
    - Exchange data
    - Building information
    - Recipe lookups
    - Company inventory management
    - Ship tracking
    """
    
    def __init__(self, credential_manager: Optional[CredentialManager] = None):
        """Initialize MCP Server
        
        Args:
            credential_manager: Optional credential manager instance
        """
        self.credential_manager = credential_manager or CredentialManager()
        self.multi_company_fio: Optional[MultiCompanyFIO] = None
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register MCP tools
        
        Returns:
            Dictionary of tool definitions
        """
        return {
            "get_material": {
                "description": "Get information about a material by ticker or name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Material ticker symbol"}
                    },
                    "required": ["ticker"]
                }
            },
            "get_planet": {
                "description": "Get information about a planet by natural ID or name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "planet_id": {"type": "string", "description": "Planet natural ID or name"}
                    },
                    "required": ["planet_id"]
                }
            },
            "get_exchange_data": {
                "description": "Get commodity exchange data for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Exchange ticker symbol"}
                    },
                    "required": ["ticker"]
                }
            },
            "get_company_inventory": {
                "description": "Get inventory for a specific company",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "company_code": {"type": "string", "description": "Company code"}
                    },
                    "required": ["company_code"]
                }
            },
            "get_company_planets": {
                "description": "Get planets owned or operated by a company",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "company_code": {"type": "string", "description": "Company code"}
                    },
                    "required": ["company_code"]
                }
            },
            "get_company_ships": {
                "description": "Get ships owned by a company",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "company_code": {"type": "string", "description": "Company code"}
                    },
                    "required": ["company_code"]
                }
            },
            "add_company": {
                "description": "Add a new company with API credentials",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "company_code": {"type": "string", "description": "Unique company code"},
                        "company_name": {"type": "string", "description": "Company display name"},
                        "api_key": {"type": "string", "description": "Primary API key"},
                        "api_key2": {"type": "string", "description": "Secondary API key (optional)"},
                        "username": {"type": "string", "description": "FIO username for API calls (distinct from company name, required for Sites/Storage endpoints)"}
                    },
                    "required": ["company_code", "company_name", "api_key", "username"]
                }
            },
            "switch_company": {
                "description": "Switch to a different active company",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "company_code": {"type": "string", "description": "Company code to switch to"}
                    },
                    "required": ["company_code"]
                }
            },
            "list_companies": {
                "description": "List all registered companies",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    def initialize_multi_company(self) -> None:
        """Initialize multi-company FIO instance with stored credentials"""
        if self.multi_company_fio is None:
            self.multi_company_fio = MultiCompanyFIO(self.credential_manager)
    
    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP tool call
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        try:
            if tool_name not in self.tools:
                return {"error": f"Unknown tool: {tool_name}"}
            
            # Route to appropriate handler
            handler = getattr(self, f"_handle_{tool_name}", None)
            if handler is None:
                return {"error": f"No handler for tool: {tool_name}"}
            
            return handler(arguments)
        
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return {"error": str(e)}
    
    def _handle_get_material(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_material tool call"""
        ticker = args.get("ticker")
        self.initialize_multi_company()
        
        fio = self.multi_company_fio.get_active_fio()
        if fio is None:
            return {"error": "No active company configured"}
        
        material = fio.Material.get(ticker)
        return {"result": material.model_dump() if material else None}
    
    def _handle_get_planet(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_planet tool call"""
        planet_id = args.get("planet_id")
        self.initialize_multi_company()
        
        fio = self.multi_company_fio.get_active_fio()
        if fio is None:
            return {"error": "No active company configured"}
        
        planet = fio.Planet.get(planet_id)
        return {"result": planet.model_dump() if planet else None}
    
    def _handle_get_exchange_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_exchange_data tool call"""
        ticker = args.get("ticker")
        self.initialize_multi_company()
        
        fio = self.multi_company_fio.get_active_fio()
        if fio is None:
            return {"error": "No active company configured"}
        
        exchange = fio.Exchange.get(ticker)
        return {"result": exchange.model_dump() if exchange else None}
    
    def _handle_get_company_inventory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_company_inventory tool call"""
        company_code = args.get("company_code")
        self.initialize_multi_company()
        
        company_data = self.multi_company_fio.get_company_data(company_code)
        if company_data is None:
            return {"error": f"Company {company_code} not found"}
        
        return {"result": [item.model_dump() for item in company_data.Inventory]}
    
    def _handle_get_company_planets(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_company_planets tool call"""
        company_code = args.get("company_code")
        self.initialize_multi_company()
        
        company_data = self.multi_company_fio.get_company_data(company_code)
        if company_data is None:
            return {"error": f"Company {company_code} not found"}
        
        return {"result": [planet.model_dump() for planet in company_data.Planets]}
    
    def _handle_get_company_ships(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_company_ships tool call"""
        company_code = args.get("company_code")
        self.initialize_multi_company()
        
        company_data = self.multi_company_fio.get_company_data(company_code)
        if company_data is None:
            return {"error": f"Company {company_code} not found"}
        
        return {"result": [ship.model_dump() for ship in company_data.Ships]}
    
    def _handle_add_company(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_company tool call"""
        company_code = args.get("company_code")
        company_name = args.get("company_name")
        api_key = args.get("api_key")
        api_key2 = args.get("api_key2")
        username = args.get("username")
        
        # Store credentials (including username)
        success = self.credential_manager.store_credentials(
            company_code, api_key, api_key2, username=username
        )
        if not success:
            return {"error": "Failed to store credentials"}
        
        # Initialize multi-company if needed
        self.initialize_multi_company()
        
        # Add company
        self.multi_company_fio.add_company(
            company_code, company_name, api_key, api_key2, username=username
        )
        
        return {"result": f"Company {company_code} added successfully"}
    
    def _handle_switch_company(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle switch_company tool call"""
        company_code = args.get("company_code")
        self.initialize_multi_company()
        
        success = self.multi_company_fio.set_active_company(company_code)
        if not success:
            return {"error": f"Company {company_code} not found"}
        
        return {"result": f"Switched to company {company_code}"}
    
    def _handle_list_companies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_companies tool call"""
        companies = self.credential_manager.list_companies()
        return {"result": companies}
    
    def get_tools_manifest(self) -> List[Dict[str, Any]]:
        """Get the MCP tools manifest
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for name, tool in self.tools.items()
        ]
