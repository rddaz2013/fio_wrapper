# Multi-Company Management

The FIO Wrapper now supports managing multiple companies, each with their own API keys and data structures for planets, inventory, and ships.

## Overview

The multi-company feature allows you to:
- Register and manage multiple companies with different API credentials
- Switch between companies seamlessly
- Track company-specific data (inventory, planets, ships)
- Access FIO API with different credentials for each company

## Quick Start

```python
from fio_wrapper import MultiCompanyFIO, CredentialManager

# Initialize credential manager
cred_mgr = CredentialManager()

# Initialize multi-company FIO
multi_fio = MultiCompanyFIO(cred_mgr)

# Add companies
multi_fio.add_company(
    company_code="COMP1",
    company_name="Company One",
    api_key="your_api_key_here",
    api_key2="your_second_api_key_here"  # Optional
)

multi_fio.add_company(
    company_code="COMP2",
    company_name="Company Two",
    api_key="another_api_key"
)

# Switch to a specific company
multi_fio.set_active_company("COMP1")

# Access FIO API for the active company
fio = multi_fio.get_active_fio()
material = fio.Material.get("DW")
print(material)
```

## Company Data Structures

### Inventory Items

Each company can track inventory items with the following structure:

```python
from fio_wrapper.models.company_models import InventoryItem

inventory_item = InventoryItem(
    MaterialTicker="DW",
    MaterialName="Drinking Water",
    Quantity=100.0,
    StorageId="storage_id",
    LocationName="Planet XYZ"
)
```

### Planet Information

Track planets owned or operated by a company:

```python
from fio_wrapper.models.company_models import PlanetInfo

planet = PlanetInfo(
    PlanetNaturalId="ABC-123",
    PlanetName="My Planet",
    Gravity=1.0,
    Temperature=20.0,
    HasLocalMarket=True,
    HasWarehouse=True
)
```

### Ship Information

Track ships owned by a company:

```python
from fio_wrapper.models.company_models import ShipInfo

ship = ShipInfo(
    ShipName="Cargo Runner",
    ShipType="Freighter",
    Location="Planet XYZ",
    CargoCapacity=1000.0,
    Status="Docked"
)
```

## Managing Company Data

### Update Inventory

```python
inventory_data = [
    {
        "MaterialTicker": "DW",
        "Quantity": 100.0,
        "LocationName": "Planet A"
    },
    {
        "MaterialTicker": "RAT",
        "Quantity": 50.0,
        "LocationName": "Planet B"
    }
]

multi_fio.update_company_inventory("COMP1", inventory_data)
```

### Update Planets

```python
planets_data = [
    {
        "PlanetNaturalId": "ABC-123",
        "PlanetName": "Home Base",
        "HasWarehouse": True
    }
]

multi_fio.update_company_planets("COMP1", planets_data)
```

### Update Ships

```python
ships_data = [
    {
        "ShipName": "Cargo Runner 1",
        "ShipType": "Freighter",
        "Status": "In Transit"
    }
]

multi_fio.update_company_ships("COMP1", ships_data)
```

## Retrieving Company Data

```python
# Get company data
company_data = multi_fio.get_company_data("COMP1")

print(f"Company: {company_data.CompanyName}")
print(f"Inventory items: {len(company_data.Inventory)}")
print(f"Planets: {len(company_data.Planets)}")
print(f"Ships: {len(company_data.Ships)}")

# Access specific data
for item in company_data.Inventory:
    print(f"Material: {item.MaterialTicker}, Quantity: {item.Quantity}")
```

## Best Practices

1. **Secure Storage**: Always use the CredentialManager for storing API keys securely
2. **Environment Variables**: For production, consider using environment variables for API keys
3. **Regular Updates**: Update company data regularly to keep it current
4. **Error Handling**: Always check return values when adding or updating companies
5. **Active Company**: Set an active company before performing operations
