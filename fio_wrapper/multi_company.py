"""Multi-company management for FIO Wrapper

This module provides functionality to manage multiple companies,
each with their own API keys and data.
"""
import logging
from typing import Dict, Optional
from fio_wrapper.fio import FIO
from fio_wrapper.credentials import CredentialManager
from fio_wrapper.models.company_models import CompanyData, MultiCompanyConfig

logger = logging.getLogger(__name__)


class MultiCompanyFIO:
    """Manages multiple FIO instances for different companies
    
    This class allows you to:
    - Register multiple companies with different API keys
    - Switch between companies
    - Manage company-specific data (inventory, planets, ships)
    - Access FIO API with different credentials
    
    Example:
        >>> from fio_wrapper.multi_company import MultiCompanyFIO
        >>> from fio_wrapper.credentials import CredentialManager
        >>> 
        >>> cred_mgr = CredentialManager()
        >>> multi_fio = MultiCompanyFIO(cred_mgr)
        >>> 
        >>> # Add companies (username is the FIO login name, distinct from company_name)
        >>> multi_fio.add_company("COMP1", "Company One", "api_key_1", username="player1")
        >>> multi_fio.add_company("COMP2", "Company Two", "api_key_2", username="player2")
        >>> 
        >>> # Switch between companies
        >>> multi_fio.set_active_company("COMP1")
        >>> material = multi_fio.get_active_fio().Material.get("DW")
        >>> 
        >>> # Get the FIO username for API calls that need it
        >>> username = multi_fio.get_active_username()
        >>> sites = multi_fio.get_active_fio().Sites.planets(username=username)
    """
    
    def __init__(self, credential_manager: CredentialManager):
        """Initialize multi-company FIO manager
        
        Args:
            credential_manager: Credential manager instance
        """
        self.credential_manager = credential_manager
        self.config = MultiCompanyConfig()
        self.fio_instances: Dict[str, FIO] = {}
        
        # Load companies from stored credentials
        self._load_companies()
    
    def _load_companies(self) -> None:
        """Load companies from stored credentials"""
        company_codes = self.credential_manager.list_companies()
        
        for company_code in company_codes:
            api_key, api_key2, username = self.credential_manager.get_credentials(company_code)
            if api_key:
                # Create CompanyData object
                company_data = CompanyData(
                    CompanyName=company_code,  # Will be updated when we fetch company info
                    CompanyCode=company_code,
                    Username=username
                )
                self.config.add_company(company_code, company_data)
                
                # Create FIO instance
                self.fio_instances[company_code] = FIO(api_key=api_key)
                
                logger.info(f"Loaded company: {company_code}")
    
    def add_company(self, company_code: str, company_name: str, 
                   api_key: str, api_key2: Optional[str] = None,
                   username: Optional[str] = None) -> bool:
        """Add a new company
        
        Args:
            company_code: Unique company code
            company_name: Company display name
            api_key: Primary API key
            api_key2: Secondary API key (optional)
            username: FIO username for API calls (optional). This is the
                      actual FIO account username, which is distinct from
                      the company name. Required for endpoints like
                      /sites/planets/{username} and /storage/{username}.
            
        Returns:
            True if successful
        """
        try:
            # Store credentials (including username)
            self.credential_manager.store_credentials(
                company_code, api_key, api_key2, username=username
            )
            
            # Create company data
            company_data = CompanyData(
                CompanyName=company_name,
                CompanyCode=company_code,
                Username=username
            )
            self.config.add_company(company_code, company_data)
            
            # Create FIO instance
            self.fio_instances[company_code] = FIO(api_key=api_key)
            
            logger.info(f"Added company: {company_code}")
            return True
        
        except Exception as e:
            logger.error(f"Error adding company {company_code}: {e}")
            return False
    
    def remove_company(self, company_code: str) -> bool:
        """Remove a company
        
        Args:
            company_code: Company code to remove
            
        Returns:
            True if successful
        """
        try:
            # Delete credentials
            self.credential_manager.delete_credentials(company_code)
            
            # Remove from config
            if company_code in self.config.companies:
                del self.config.companies[company_code]
            
            # Remove FIO instance
            if company_code in self.fio_instances:
                del self.fio_instances[company_code]
            
            # Reset active company if it was the one removed
            if self.config.active_company == company_code:
                self.config.active_company = None
                if self.config.companies:
                    self.config.active_company = list(self.config.companies.keys())[0]
            
            logger.info(f"Removed company: {company_code}")
            return True
        
        except Exception as e:
            logger.error(f"Error removing company {company_code}: {e}")
            return False
    
    def set_active_company(self, company_code: str) -> bool:
        """Set the active company
        
        Args:
            company_code: Company code to set as active
            
        Returns:
            True if successful
        """
        return self.config.set_active_company(company_code)
    
    def get_active_company(self) -> Optional[CompanyData]:
        """Get the active company data
        
        Returns:
            Active company data or None
        """
        return self.config.get_active_company()
    
    def get_active_fio(self) -> Optional[FIO]:
        """Get the FIO instance for the active company
        
        Returns:
            FIO instance or None
        """
        if self.config.active_company:
            return self.fio_instances.get(self.config.active_company)
        return None
    
    def get_company_data(self, company_code: str) -> Optional[CompanyData]:
        """Get company data by code
        
        Args:
            company_code: Company code
            
        Returns:
            Company data or None
        """
        return self.config.get_company(company_code)
    
    def get_company_fio(self, company_code: str) -> Optional[FIO]:
        """Get FIO instance for a specific company
        
        Args:
            company_code: Company code
            
        Returns:
            FIO instance or None
        """
        return self.fio_instances.get(company_code)
    
    def get_company_username(self, company_code: str) -> Optional[str]:
        """Get the FIO username for a specific company
        
        The username is needed for FIO API endpoints that require a user
        identifier (e.g., /sites/planets/{username}, /storage/{username}).
        This is distinct from the CompanyName.
        
        Args:
            company_code: Company code
            
        Returns:
            FIO username or None if not set
        """
        company_data = self.config.get_company(company_code)
        if company_data:
            return company_data.Username
        return None
    
    def get_active_username(self) -> Optional[str]:
        """Get the FIO username for the currently active company
        
        Returns:
            FIO username or None
        """
        if self.config.active_company:
            return self.get_company_username(self.config.active_company)
        return None
    
    def list_companies(self) -> list:
        """List all registered companies
        
        Returns:
            List of company codes
        """
        return list(self.config.companies.keys())
    
    def update_company_inventory(self, company_code: str, inventory_data: list) -> bool:
        """Update inventory data for a company
        
        Args:
            company_code: Company code
            inventory_data: List of inventory items
            
        Returns:
            True if successful
        """
        try:
            company_data = self.get_company_data(company_code)
            if company_data:
                from fio_wrapper.models.company_models import InventoryItem
                from datetime import datetime
                
                company_data.Inventory = [InventoryItem(**item) for item in inventory_data]
                company_data.LastUpdated = datetime.now()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating inventory for {company_code}: {e}")
            return False
    
    def update_company_planets(self, company_code: str, planets_data: list) -> bool:
        """Update planets data for a company
        
        Args:
            company_code: Company code
            planets_data: List of planet information
            
        Returns:
            True if successful
        """
        try:
            company_data = self.get_company_data(company_code)
            if company_data:
                from fio_wrapper.models.company_models import PlanetInfo
                from datetime import datetime
                
                company_data.Planets = [PlanetInfo(**planet) for planet in planets_data]
                company_data.LastUpdated = datetime.now()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating planets for {company_code}: {e}")
            return False
    
    def update_company_ships(self, company_code: str, ships_data: list) -> bool:
        """Update ships data for a company
        
        Args:
            company_code: Company code
            ships_data: List of ship information
            
        Returns:
            True if successful
        """
        try:
            company_data = self.get_company_data(company_code)
            if company_data:
                from fio_wrapper.models.company_models import ShipInfo
                from datetime import datetime
                
                company_data.Ships = [ShipInfo(**ship) for ship in ships_data]
                company_data.LastUpdated = datetime.now()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating ships for {company_code}: {e}")
            return False
