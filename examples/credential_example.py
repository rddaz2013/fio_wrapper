#!/usr/bin/env python3
"""Example of using the CredentialManager for secure API key storage

This example demonstrates:
- Storing API credentials securely
- Retrieving credentials from different backends
- Managing credentials for multiple companies
- Using environment variables
"""

from fio_wrapper import CredentialManager
import os
from pathlib import Path


def main():
    print("FIO Wrapper - Credential Management Example\n")
    print("=" * 50)
    
    # Example 1: Basic credential storage
    print("\n1. Basic Credential Storage")
    print("-" * 50)
    
    cred_mgr = CredentialManager()
    
    # Store credentials for a company
    success = cred_mgr.store_credentials(
        company_code="DEMO1",
        api_key="demo_api_key_12345",
        api_key2="demo_api_key_67890"
    )
    
    if success:
        print("✓ Credentials stored successfully for DEMO1")
    
    # Example 2: Retrieve credentials
    print("\n2. Retrieving Credentials")
    print("-" * 50)
    
    api_key, api_key2 = cred_mgr.get_credentials("DEMO1")
    if api_key:
        print(f"✓ Primary API Key: {api_key[:10]}...")
        if api_key2:
            print(f"✓ Secondary API Key: {api_key2[:10]}...")
    else:
        print("✗ No credentials found")
    
    # Example 3: Using environment variables
    print("\n3. Environment Variables")
    print("-" * 50)
    
    # Set environment variables
    os.environ["FIO_API_KEY_ENVCO"] = "env_api_key_abc"
    os.environ["FIO_API_KEY2_ENVCO"] = "env_api_key_xyz"
    
    # Environment variables take priority
    env_key1, env_key2 = cred_mgr.get_credentials("ENVCO")
    if env_key1:
        print(f"✓ Retrieved from environment: {env_key1[:10]}...")
    
    # Example 4: List all companies
    print("\n4. Listing Companies")
    print("-" * 50)
    
    companies = cred_mgr.list_companies()
    print(f"Companies with stored credentials: {companies}")
    
    # Example 5: Custom configuration directory
    print("\n5. Custom Configuration")
    print("-" * 50)
    
    custom_dir = Path("/tmp/fio_wrapper_custom")
    custom_cred_mgr = CredentialManager(config_dir=custom_dir)
    
    custom_cred_mgr.store_credentials(
        company_code="CUSTOM",
        api_key="custom_api_key"
    )
    print(f"✓ Credentials stored in custom directory: {custom_dir}")
    
    # Example 6: Delete credentials
    print("\n6. Deleting Credentials")
    print("-" * 50)
    
    success = cred_mgr.delete_credentials("DEMO1")
    if success:
        print("✓ Credentials deleted for DEMO1")
    
    # Verify deletion
    api_key, _ = cred_mgr.get_credentials("DEMO1")
    if not api_key:
        print("✓ Confirmed: Credentials no longer exist")
    
    # Example 7: Storage backends info
    print("\n7. Storage Backend Information")
    print("-" * 50)
    
    print("\nCredentials are checked in this order:")
    print("1. Environment variables (FIO_API_KEY_<CODE>)")
    print("2. System keyring (if available)")
    print("3. Encrypted file (~/.fio_wrapper/credentials.enc)")
    
    print("\nFile locations:")
    print(f"  Config directory: {cred_mgr.config_dir}")
    print(f"  Credentials file: {cred_mgr.credentials_file}")
    print(f"  Encryption key: {cred_mgr.config_dir / '.key'}")
    
    if cred_mgr.use_keyring:
        print("\n✓ System keyring is available and will be used")
    else:
        print("\n⚠ System keyring not available (install: pip install keyring)")
    
    # Example 8: Best practices
    print("\n8. Security Best Practices")
    print("-" * 50)
    
    print("""
    ✓ Never commit API keys to version control
    ✓ Use environment variables in production
    ✓ Encrypted files have 0600 permissions (owner only)
    ✓ Back up your encryption key securely
    ✓ Rotate API keys regularly
    ✓ Use different keys for development and production
    """)
    
    # Clean up
    print("\n9. Cleanup")
    print("-" * 50)
    
    # Clean up environment variables
    if "FIO_API_KEY_ENVCO" in os.environ:
        del os.environ["FIO_API_KEY_ENVCO"]
    if "FIO_API_KEY2_ENVCO" in os.environ:
        del os.environ["FIO_API_KEY2_ENVCO"]
    
    print("✓ Cleaned up environment variables")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!\n")


if __name__ == "__main__":
    main()
