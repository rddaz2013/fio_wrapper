# Multi-Company and MCP Support

This document describes the new multi-company management and MCP (Model Context Protocol) server features added to FIO Wrapper.

## New Features

### 1. Multi-Company Management

Manage multiple companies with separate API keys and track company-specific data:

- **Multiple API Keys**: Store and manage two API keys per company
- **Company Data Structures**: Track inventory, planets, and ships for each company
- **Secure Storage**: Encrypted credential storage with multiple backend options
- **Easy Switching**: Switch between companies seamlessly

### 2. MCP Server Integration

FIO Wrapper can now function as an MCP server, providing tools for AI assistants:

- **9 MCP Tools**: Access FIO data through standardized MCP protocol
- **AI Integration**: Compatible with Claude, ChatGPT, and other MCP clients
- **Real-time Data**: Access game data in real-time through natural language
- **Multi-Company Tools**: Manage multiple companies through MCP interface

### 3. Secure Credential Management

Advanced credential management with multiple storage options:

- **Environment Variables**: For development and temporary use
- **Encrypted Files**: AES encryption with Fernet for secure local storage
- **System Keyring**: Optional integration with OS credential stores
- **Automatic Fallback**: Priority-based credential retrieval

## Installation

Install with the new dependencies:

```bash
pip install fio-wrapper cryptography keyring
```

Or from source:

```bash
git clone https://github.com/rddaz2013/fio_wrapper.git
cd fio_wrapper
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Basic Multi-Company Usage

```python
from fio_wrapper import MultiCompanyFIO, CredentialManager

# Initialize
cred_mgr = CredentialManager()
multi_fio = MultiCompanyFIO(cred_mgr)

# Add your first company
multi_fio.add_company(
    company_code="MYCO",
    company_name="My Company",
    api_key="your_fio_api_key",
    api_key2="your_second_api_key"  # Optional
)

# Use FIO as normal
fio = multi_fio.get_active_fio()
material = fio.Material.get("DW")
print(material)
```

### Using MCP Server

```python
from fio_wrapper import MCPServer, CredentialManager

# Initialize MCP server
cred_mgr = CredentialManager()
mcp_server = MCPServer(cred_mgr)

# Get material data
result = mcp_server.handle_tool_call(
    "get_material",
    {"ticker": "DW"}
)
print(result)
```

## Architecture

### Component Overview

```
fio_wrapper/
├── credentials.py          # Secure credential management
├── multi_company.py        # Multi-company FIO manager
├── mcp_server.py          # MCP server implementation
└── models/
    └── company_models.py  # Data models for companies
```

### Data Flow

```
User → MultiCompanyFIO → CredentialManager → Encrypted Storage
                      ↓
                     FIO → API Endpoints
```

### MCP Integration

```
MCP Client → MCPServer → MultiCompanyFIO → FIO → FNAR API
```

## API Key Management

### Two API Keys Per Company

The FNAR API supports two API keys per user/company:

1. **Primary API Key**: Main authentication for most endpoints
2. **Secondary API Key**: Optional, for specific authenticated endpoints

### Storing Credentials

```python
from fio_wrapper import CredentialManager

cred_mgr = CredentialManager()

# Store both keys
cred_mgr.store_credentials(
    company_code="COMP1",
    api_key="primary_key_here",
    api_key2="secondary_key_here"
)

# Retrieve keys
api_key, api_key2 = cred_mgr.get_credentials("COMP1")
```

### Environment Variables

Set via environment:

```bash
export FIO_API_KEY_COMP1="primary_key"
export FIO_API_KEY2_COMP1="secondary_key"
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Multi-Company Management](docs/multi_company.md)**: Complete guide to managing multiple companies
- **[Credential Management](docs/credentials.md)**: Secure credential storage and retrieval
- **[MCP Server](docs/mcp_server.md)**: MCP server setup and integration

## Examples

See the `examples/` directory for complete working examples:

- `multi_company_example.py`: Basic multi-company usage
- `mcp_server_example.py`: Standalone MCP server
- `credential_example.py`: Credential management examples

## Migration Guide

### From Single-Company to Multi-Company

Old code:
```python
from fio_wrapper import FIO

fio = FIO(api_key="your_key")
material = fio.Material.get("DW")
```

New code:
```python
from fio_wrapper import MultiCompanyFIO, CredentialManager

cred_mgr = CredentialManager()
multi_fio = MultiCompanyFIO(cred_mgr)
multi_fio.add_company("MYCO", "My Company", "your_key")

fio = multi_fio.get_active_fio()
material = fio.Material.get("DW")
```

The FIO interface remains the same - only the initialization changes.

## Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** in production
3. **Encrypt credential files** are stored at `~/.fio_wrapper/credentials.enc`
4. **File permissions** are automatically set to 0600 (owner read/write only)
5. **Keyring integration** provides OS-level security when available

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

When contributing to multi-company features:
- Add tests for new credential storage backends
- Update documentation for new MCP tools
- Ensure backward compatibility with single-company usage

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://prunplanner.github.io/fio_wrapper/
- **Issues**: https://github.com/rddaz2013/fio_wrapper/issues
- **FIO API Docs**: https://doc.fnar.net/

## Changelog

### Version 2.0.0 (Multi-Company Update)

**New Features:**
- Multi-company management with separate API keys
- MCP server implementation for AI assistant integration
- Secure credential management with encryption
- Company data structures for inventory, planets, and ships
- Environment variable and keyring support

**Breaking Changes:**
- None - fully backward compatible with single-company usage

**Dependencies Added:**
- `cryptography >= 41.0.0`
- `keyring >= 24.0.0` (optional)
