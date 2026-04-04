"""Secure credential management for FIO Wrapper

This module provides secure storage and retrieval of API keys for multiple
companies/users. It supports:
- Environment variables
- Encrypted configuration files
- Keyring integration (if available)
"""
import os
import json
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages secure storage and retrieval of API credentials
    
    This class supports multiple storage backends:
    1. Environment variables (FIO_API_KEY_<COMPANY_CODE>, FIO_API_KEY2_<COMPANY_CODE>)
    2. Encrypted JSON file (~/.fio_wrapper/credentials.enc)
    3. System keyring (if keyring package is installed)
    
    Each company can have two API keys for different purposes.
    """
    
    def __init__(self, config_dir: Optional[Path] = None, encryption_key: Optional[str] = None):
        """Initialize the credential manager
        
        Args:
            config_dir: Directory for storing encrypted credentials
            encryption_key: Optional encryption key (if not provided, generates from system)
        """
        self.config_dir = config_dir or Path.home() / ".fio_wrapper"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.config_dir / "credentials.enc"
        
        # Initialize encryption
        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            # Generate a key based on machine-specific information
            # In production, you might want to use a password-based key derivation
            self.encryption_key = self._get_or_create_key()
        
        self.cipher = Fernet(self.encryption_key)
        
        # Try to import keyring for system credential storage
        try:
            import keyring
            self.keyring = keyring
            self.use_keyring = True
        except ImportError:
            self.keyring = None
            self.use_keyring = False
            logger.info("Keyring not available. Using encrypted file storage.")
    
    def _get_or_create_key(self) -> bytes:
        """Get or create an encryption key
        
        Returns:
            Fernet-compatible encryption key
        """
        key_file = self.config_dir / ".key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate a new key
            key = Fernet.generate_key()
            # Securely save the key with restricted permissions
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set file permissions to be readable only by owner
            os.chmod(key_file, 0o600)
            return key
    
    def store_credentials(self, company_code: str, api_key: str, api_key2: Optional[str] = None) -> bool:
        """Store API credentials for a company
        
        Args:
            company_code: Unique company identifier
            api_key: Primary API key
            api_key2: Secondary API key (optional)
            
        Returns:
            True if successful
        """
        try:
            # Load existing credentials
            credentials = self._load_credentials_file()
            
            # Store credentials
            credentials[company_code] = {
                "api_key": api_key,
                "api_key2": api_key2
            }
            
            # Save to encrypted file
            self._save_credentials_file(credentials)
            
            # Also try to save to keyring if available
            if self.use_keyring:
                try:
                    self.keyring.set_password("fio_wrapper", f"{company_code}_key1", api_key)
                    if api_key2:
                        self.keyring.set_password("fio_wrapper", f"{company_code}_key2", api_key2)
                except Exception as e:
                    logger.warning(f"Could not save to keyring: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error storing credentials: {e}")
            return False
    
    def get_credentials(self, company_code: str) -> Tuple[Optional[str], Optional[str]]:
        """Retrieve API credentials for a company
        
        Checks in order:
        1. Environment variables
        2. System keyring
        3. Encrypted file
        
        Args:
            company_code: Company identifier
            
        Returns:
            Tuple of (api_key, api_key2)
        """
        # Check environment variables first
        env_key1 = os.environ.get(f"FIO_API_KEY_{company_code.upper()}")
        env_key2 = os.environ.get(f"FIO_API_KEY2_{company_code.upper()}")
        
        if env_key1:
            return (env_key1, env_key2)
        
        # Check keyring
        if self.use_keyring:
            try:
                key1 = self.keyring.get_password("fio_wrapper", f"{company_code}_key1")
                key2 = self.keyring.get_password("fio_wrapper", f"{company_code}_key2")
                if key1:
                    return (key1, key2)
            except Exception as e:
                logger.warning(f"Could not retrieve from keyring: {e}")
        
        # Check encrypted file
        try:
            credentials = self._load_credentials_file()
            company_creds = credentials.get(company_code, {})
            return (company_creds.get("api_key"), company_creds.get("api_key2"))
        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            return (None, None)
    
    def delete_credentials(self, company_code: str) -> bool:
        """Delete credentials for a company
        
        Args:
            company_code: Company identifier
            
        Returns:
            True if successful
        """
        try:
            # Remove from file
            credentials = self._load_credentials_file()
            if company_code in credentials:
                del credentials[company_code]
                self._save_credentials_file(credentials)
            
            # Remove from keyring
            if self.use_keyring:
                try:
                    self.keyring.delete_password("fio_wrapper", f"{company_code}_key1")
                    self.keyring.delete_password("fio_wrapper", f"{company_code}_key2")
                except Exception:
                    pass
            
            return True
        except Exception as e:
            logger.error(f"Error deleting credentials: {e}")
            return False
    
    def list_companies(self) -> list:
        """List all companies with stored credentials
        
        Returns:
            List of company codes
        """
        try:
            credentials = self._load_credentials_file()
            return list(credentials.keys())
        except Exception:
            return []
    
    def _load_credentials_file(self) -> Dict:
        """Load and decrypt credentials file
        
        Returns:
            Dictionary of credentials
        """
        if not self.credentials_file.exists():
            return {}
        
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Error loading credentials file: {e}")
            return {}
    
    def _save_credentials_file(self, credentials: Dict) -> None:
        """Encrypt and save credentials file
        
        Args:
            credentials: Dictionary of credentials to save
        """
        try:
            json_data = json.dumps(credentials).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions
            os.chmod(self.credentials_file, 0o600)
        except Exception as e:
            logger.error(f"Error saving credentials file: {e}")
            raise
