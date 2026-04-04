#!/usr/bin/env python3
"""Example of using FIO Wrapper with multi-company support

This example demonstrates:
- Adding multiple companies
- Switching between companies
- Managing company-specific data
- Accessing FIO API with different credentials
"""

from fio_wrapper import MultiCompanyFIO, CredentialManager
import os


def main():
    print("FIO Wrapper - Multi-Company Example\n")
    print("=" * 50)
    
    # Initialize credential manager
    cred_mgr = CredentialManager()
    
    # Initialize multi-company FIO
    multi_fio = MultiCompanyFIO(cred_mgr)
    
    # Example 1: Add companies
    print("\n1. Adding Companies")
    print("-" * 50)
    
    # You can use environment variables for API keys
    api_key_1 = os.environ.get("FIO_API_KEY_COMPANY1", "demo_key_1")
    api_key_2 = os.environ.get("FIO_API_KEY_COMPANY2", "demo_key_2")
    
    multi_fio.add_company(
        company_code="COMP1",
        company_name="Mining Corporation",
        api_key=api_key_1
    )
    print("✓ Added COMP1: Mining Corporation")
    
    multi_fio.add_company(
        company_code="COMP2",
        company_name="Trading Empire",
        api_key=api_key_2
    )
    print("✓ Added COMP2: Trading Empire")
    
    # Example 2: List companies
    print("\n2. Listing Companies")
    print("-" * 50)
    companies = multi_fio.list_companies()
    print(f"Registered companies: {companies}")
    
    # Example 3: Switch between companies
    print("\n3. Switching Companies")
    print("-" * 50)
    
    multi_fio.set_active_company("COMP1")
    active = multi_fio.get_active_company()
    print(f"Active company: {active.CompanyName} ({active.CompanyCode})")
    
    # Example 4: Access FIO API for active company
    print("\n4. Accessing FIO API")
    print("-" * 50)
    
    fio = multi_fio.get_active_fio()
    if fio:
        try:
            material = fio.Material.get("DW")
            print(f"Material: {material.Name}")
            print(f"Ticker: {material.Ticker}")
            print(f"Weight: {material.Weight}")
            print(f"Volume: {material.Volume}")
        except Exception as e:
            print(f"Note: API call requires valid API key. Error: {e}")
    
    # Example 5: Update company inventory
    print("\n5. Updating Company Inventory")
    print("-" * 50)
    
    inventory_data = [
        {
            "MaterialTicker": "DW",
            "Quantity": 100.0,
            "LocationName": "Mining Station Alpha"
        },
        {
            "MaterialTicker": "RAT",
            "Quantity": 50.0,
            "LocationName": "Mining Station Alpha"
        }
    ]
    
    success = multi_fio.update_company_inventory("COMP1", inventory_data)
    if success:
        print("✓ Updated inventory for COMP1")
        company_data = multi_fio.get_company_data("COMP1")
        print(f"  Total inventory items: {len(company_data.Inventory)}")
        for item in company_data.Inventory:
            print(f"  - {item.MaterialTicker}: {item.Quantity} @ {item.LocationName}")
    
    # Example 6: Update company planets
    print("\n6. Updating Company Planets")
    print("-" * 50)
    
    planets_data = [
        {
            "PlanetNaturalId": "UV-351",
            "PlanetName": "Mining World",
            "HasWarehouse": True,
            "HasLocalMarket": True
        }
    ]
    
    success = multi_fio.update_company_planets("COMP1", planets_data)
    if success:
        print("✓ Updated planets for COMP1")
        company_data = multi_fio.get_company_data("COMP1")
        print(f"  Total planets: {len(company_data.Planets)}")
        for planet in company_data.Planets:
            print(f"  - {planet.PlanetName} ({planet.PlanetNaturalId})")
    
    # Example 7: Update company ships
    print("\n7. Updating Company Ships")
    print("-" * 50)
    
    ships_data = [
        {
            "ShipName": "Ore Hauler 1",
            "ShipType": "Freighter",
            "Status": "In Transit",
            "CargoCapacity": 1000.0
        },
        {
            "ShipName": "Ore Hauler 2",
            "ShipType": "Freighter",
            "Status": "Docked",
            "Location": "Mining Station Alpha",
            "CargoCapacity": 1000.0
        }
    ]
    
    success = multi_fio.update_company_ships("COMP1", ships_data)
    if success:
        print("✓ Updated ships for COMP1")
        company_data = multi_fio.get_company_data("COMP1")
        print(f"  Total ships: {len(company_data.Ships)}")
        for ship in company_data.Ships:
            print(f"  - {ship.ShipName} ({ship.ShipType}): {ship.Status}")
    
    # Example 8: Work with second company
    print("\n8. Switching to Second Company")
    print("-" * 50)
    
    multi_fio.set_active_company("COMP2")
    print("✓ Switched to COMP2: Trading Empire")
    
    # You can also get FIO instance directly
    fio_comp2 = multi_fio.get_company_fio("COMP2")
    print("✓ Got FIO instance for COMP2")
    
    # Example 9: Summary
    print("\n9. Summary")
    print("-" * 50)
    print(f"Total companies managed: {len(multi_fio.list_companies())}")
    
    for company_code in multi_fio.list_companies():
        company_data = multi_fio.get_company_data(company_code)
        print(f"\n{company_data.CompanyName} ({company_code}):")
        print(f"  Inventory items: {len(company_data.Inventory)}")
        print(f"  Planets: {len(company_data.Planets)}")
        print(f"  Ships: {len(company_data.Ships)}")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!\n")


if __name__ == "__main__":
    main()
