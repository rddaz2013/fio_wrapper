# Secure Credential Management

The FIO Wrapper includes a robust credential management system for securely storing and retrieving API keys for multiple companies.

## Overview

The CredentialManager class provides secure storage through multiple backends:

1. **Environment Variables** - For temporary or development use
2. **Encrypted File Storage** - Default secure storage using Fernet encryption
3. **System Keyring** - Optional integration with system credential stores

## Quick Start

```python
from fio_wrapper import CredentialManager

# Initialize credential manager
cred_mgr = CredentialManager()

# Store credentials for a company
cred_mgr.store_credentials(
    company_code="COMP1",
    api_key="your_api_key_here",
    api_key2="your_second_api_key_here"  # Optional
)

# Retrieve credentials
api_key, api_key2 = cred_mgr.get_credentials("COMP1")
print(f"API Key: {api_key}")
```

## Storage Backends

### Environment Variables

The credential manager first checks environment variables for API keys:

```bash
# Set environment variables
export FIO_API_KEY_COMP1="your_api_key_here"
export FIO_API_KEY2_COMP1="your_second_api_key_here"
```

Environment variable format:
- Primary key: `FIO_API_KEY_<COMPANY_CODE>`
- Secondary key: `FIO_API_KEY2_<COMPANY_CODE>`

### Encrypted File Storage

By default, credentials are stored in an encrypted file at `~/.fio_wrapper/credentials.enc`.

**Features:**
- AES encryption using Fernet (symmetric encryption)
- Automatic key generation and secure storage
- Restricted file permissions (0600 - owner read/write only)
- Separate encryption key stored at `~/.fio_wrapper/.key`

**Custom Configuration:**

```python
from pathlib import Path

# Use custom directory
cred_mgr = CredentialManager(
    config_dir=Path("/custom/path/.fio_wrapper")
)

# Use custom encryption key
cred_mgr = CredentialManager(
    encryption_key="your_custom_32_byte_key_here"
)
```

### System Keyring (Optional)

If the keyring package is installed, credentials are also stored in the system's credential store:

```bash
# Install keyring support
pip install keyring
```

## API Reference

### Store Credentials

```python
success = cred_mgr.store_credentials(
    company_code="COMP1",
    api_key="primary_key",
    api_key2="secondary_key"  # Optional
)

if success:
    print("Credentials stored successfully")
```

### Retrieve Credentials

```python
api_key, api_key2 = cred_mgr.get_credentials("COMP1")

if api_key:
    print(f"Found API key for COMP1")
else:
    print("No credentials found")
```

**Retrieval Priority:**
1. Environment variables
2. System keyring (if available)
3. Encrypted file

### Delete Credentials

```python
success = cred_mgr.delete_credentials("COMP1")

if success:
    print("Credentials deleted from all storage backends")
```

### List Companies

```python
companies = cred_mgr.list_companies()
print(f"Companies with stored credentials: {companies}")
```

## Security Best Practices

1. **File Permissions**: The credential manager automatically sets restrictive permissions on credential files
2. **Environment Variables**: For development or temporary use only
3. **Production Deployment**: Use environment variables set via deployment platform
4. **Key Rotation**: Regularly rotate API keys
5. **Encryption Key**: The encryption key at `~/.fio_wrapper/.key` is critical - back it up securely

## API Keys in FIO/FNAR

The FIO/FNAR API supports two API keys per user/company:

1. **Primary API Key** - Main authentication key
2. **Secondary API Key** - Optional, for specific endpoints or additional permissions

Generate API keys from your FIO account and store securely using the CredentialManager.
