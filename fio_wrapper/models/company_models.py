"""Company models for FIO Wrapper

This module contains data models for managing company information,
including inventory, planets, and ships.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class InventoryItem(BaseModel):
    """Model for a single inventory item"""
    MaterialTicker: str
    MaterialName: Optional[str] = None
    MaterialId: Optional[str] = None
    Quantity: float
    Type: Optional[str] = None
    Value: Optional[float] = None
    StorageId: Optional[str] = None
    LocationName: Optional[str] = None
    LocationNaturalId: Optional[str] = None
    Timestamp: Optional[datetime] = None


class PlanetInfo(BaseModel):
    """Model for planet information"""
    PlanetId: Optional[str] = None
    PlanetNaturalId: str
    PlanetName: str
    Gravity: Optional[float] = None
    Temperature: Optional[float] = None
    Pressure: Optional[float] = None
    Fertility: Optional[float] = None
    Resources: Optional[List[str]] = []
    HasLocalMarket: Optional[bool] = False
    HasChamberOfCommerce: Optional[bool] = False
    HasWarehouse: Optional[bool] = False
    HasShipyard: Optional[bool] = False
    Timestamp: Optional[datetime] = None


class ShipInfo(BaseModel):
    """Model for ship information"""
    ShipId: Optional[str] = None
    ShipName: str
    ShipType: Optional[str] = None
    Registration: Optional[str] = None
    CommissionTime: Optional[datetime] = None
    Location: Optional[str] = None
    FuelStatus: Optional[Dict[str, Any]] = {}
    CargoCapacity: Optional[float] = None
    CurrentCargo: Optional[List[InventoryItem]] = []
    Status: Optional[str] = None  # e.g., "In Transit", "Docked", "Idle"
    Timestamp: Optional[datetime] = None


class CompanyData(BaseModel):
    """Model for company data including all associated information
    
    Note: CompanyName and Username are separate entities in FIO.
    CompanyName is the display name of the company, while Username
    is the FIO account username required for API endpoints like
    /sites/planets/{username} and /storage/{username}.
    """
    CompanyName: str
    CompanyCode: str
    Username: Optional[str] = None  # FIO username for API calls (distinct from CompanyName)
    CompanyId: Optional[str] = None
    Headquarters: Optional[str] = None
    Country: Optional[str] = None
    Currency: Optional[str] = None
    Employees: Optional[int] = None
    Inventory: List[InventoryItem] = []
    Planets: List[PlanetInfo] = []
    Ships: List[ShipInfo] = []
    Metadata: Optional[Dict[str, Any]] = {}
    LastUpdated: Optional[datetime] = None


class MultiCompanyConfig(BaseModel):
    """Configuration model for managing multiple companies"""
    companies: Dict[str, CompanyData] = Field(default_factory=dict)
    active_company: Optional[str] = None
    
    def add_company(self, company_code: str, company_data: CompanyData) -> None:
        """Add a company to the configuration
        
        Args:
            company_code: Unique company code
            company_data: Company data object
        """
        self.companies[company_code] = company_data
        if self.active_company is None:
            self.active_company = company_code
    
    def get_company(self, company_code: str) -> Optional[CompanyData]:
        """Get company data by code
        
        Args:
            company_code: Company code to retrieve
            
        Returns:
            Company data or None if not found
        """
        return self.companies.get(company_code)
    
    def set_active_company(self, company_code: str) -> bool:
        """Set the active company
        
        Args:
            company_code: Company code to set as active
            
        Returns:
            True if successful, False if company not found
        """
        if company_code in self.companies:
            self.active_company = company_code
            return True
        return False
    
    def get_active_company(self) -> Optional[CompanyData]:
        """Get the currently active company data
        
        Returns:
            Active company data or None
        """
        if self.active_company:
            return self.companies.get(self.active_company)
        return None
