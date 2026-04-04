#!/usr/bin/env python3
"""Beispiel: Company-Liste, Planeten und Inventory aus FIO laden

Dieses Beispiel demonstriert:
- Alle konfigurierten Companies laden und auflisten
- Für jede Company die Planetenliste der Spieler abrufen
- Für jede Company die Inventardaten von FIO abrufen
- Übersichtliche Darstellung der gesammelten Daten
"""

from fio_wrapper import MultiCompanyFIO, CredentialManager
import os


def print_header(title: str, char: str = "=", width: int = 60):
    """Gibt eine formatierte Überschrift aus."""
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def print_section(title: str, level: int = 1):
    """Gibt eine formatierte Abschnittsüberschrift aus."""
    if level == 1:
        print(f"\n{'─' * 50}")
        print(f"  {title}")
        print(f"{'─' * 50}")
    else:
        print(f"\n  ▸ {title}")


def setup_demo_companies(multi_fio: MultiCompanyFIO):
    """Erstellt Demo-Companies für das Beispiel.

    In der Praxis würden die API-Keys aus Umgebungsvariablen
    oder dem CredentialManager geladen werden.
    """
    # API-Keys aus Umgebungsvariablen lesen (oder Demo-Werte verwenden)
    api_key_1 = os.environ.get("FIO_API_KEY_COMP1", "demo_key_comp1")
    api_key_2 = os.environ.get("FIO_API_KEY_COMP2", "demo_key_comp2")

    # Company 1 hinzufügen
    multi_fio.add_company(
        company_code="MINER",
        company_name="Galactic Mining Corp",
        api_key=api_key_1,
    )
    print("  ✓ MINER: Galactic Mining Corp hinzugefügt")

    # Company 2 hinzufügen
    multi_fio.add_company(
        company_code="TRADE",
        company_name="Stellar Trading Co",
        api_key=api_key_2,
    )
    print("  ✓ TRADE: Stellar Trading Co hinzugefügt")


def demo_planeten_daten(multi_fio: MultiCompanyFIO, company_code: str):
    """Lädt und zeigt die Planetendaten für eine bestimmte Company.

    Zuerst werden die lokal gespeicherten Planeteninformationen angezeigt,
    dann wird versucht die Planetenliste über die FIO-API abzurufen.
    """
    company_data = multi_fio.get_company_data(company_code)
    if company_data is None:
        print(f"    ✗ Company {company_code} nicht gefunden")
        return

    # Lokal gespeicherte Planeten anzeigen
    if company_data.Planets:
        print(f"    Lokale Planeten ({len(company_data.Planets)}):")
        for planet in company_data.Planets:
            warehouse = "🏭 Warehouse" if planet.HasWarehouse else ""
            market = "📊 Markt" if planet.HasLocalMarket else ""
            extras = " | ".join(filter(None, [warehouse, market]))
            extras_str = f" [{extras}]" if extras else ""
            print(f"      • {planet.PlanetName} ({planet.PlanetNaturalId}){extras_str}")
    else:
        print("    Keine lokalen Planeten gespeichert.")

    # Versuch, Planeten über die FIO-API abzurufen (Sites-Endpoint)
    fio = multi_fio.get_company_fio(company_code)
    if fio:
        try:
            # Sites.planets() gibt eine Liste von SiteIds zurück
            username = company_data.CompanyName  # oder ein separater Username
            site_planets = fio.Sites.planets(username=username)
            print(f"\n    FIO Sites-Planeten ({len(site_planets)}):")
            for site_id in site_planets:
                print(f"      • Site-ID: {site_id}")
        except Exception as e:
            print(f"\n    ⚠ FIO Sites-Abfrage fehlgeschlagen: {e}")
            print("      (Gültiger API-Key erforderlich)")


def demo_inventar_daten(multi_fio: MultiCompanyFIO, company_code: str):
    """Lädt und zeigt die Inventardaten für eine bestimmte Company.

    Zuerst werden die lokal gespeicherten Inventardaten angezeigt,
    dann wird versucht die Lagerdaten über die FIO-API (Storage) abzurufen.
    """
    company_data = multi_fio.get_company_data(company_code)
    if company_data is None:
        print(f"    ✗ Company {company_code} nicht gefunden")
        return

    # Lokal gespeichertes Inventar anzeigen
    if company_data.Inventory:
        print(f"    Lokales Inventar ({len(company_data.Inventory)} Positionen):")
        # Inventar nach Standort gruppieren
        locations = {}
        for item in company_data.Inventory:
            loc = item.LocationName or "Unbekannt"
            locations.setdefault(loc, []).append(item)

        for location, items in locations.items():
            print(f"\n      📦 Standort: {location}")
            for item in items:
                name = item.MaterialName or item.MaterialTicker
                print(f"         {name}: {item.Quantity:.0f} Einheiten")
    else:
        print("    Kein lokales Inventar gespeichert.")

    # Versuch, Storage-Daten über die FIO-API abzurufen
    fio = multi_fio.get_company_fio(company_code)
    if fio:
        try:
            username = company_data.CompanyName
            storages = fio.Storage.get(username=username)
            print(f"\n    FIO Storage-Daten:")
            for storage in storages:
                name = storage.Name or storage.StorageId[:12]
                print(f"\n      🏗 Lager: {name} (Typ: {storage.Type})")
                print(f"        Gewicht: {storage.WeightCapacity} t | Volumen: {storage.VolumeCapacity} m³")
                if storage.StorageItems:
                    print(f"        Materialien ({len(storage.StorageItems)}):")
                    for si in storage.StorageItems:
                        ticker = si.MaterialTicker or "???"
                        print(f"          {ticker}: {si.MaterialAmount}x "
                              f"(Gewicht: {si.TotalWeight:.1f}, Volumen: {si.TotalVolume:.1f})")
                else:
                    print("        (leer)")
        except Exception as e:
            print(f"\n    ⚠ FIO Storage-Abfrage fehlgeschlagen: {e}")
            print("      (Gültiger API-Key erforderlich)")


def main():
    print_header("FIO Wrapper – Company-Daten, Planeten & Inventory")

    # ──────────────────────────────────────────────
    # 1. Initialisierung und Companies anlegen
    # ──────────────────────────────────────────────
    print_section("1. Companies initialisieren")

    cred_mgr = CredentialManager()
    multi_fio = MultiCompanyFIO(cred_mgr)

    setup_demo_companies(multi_fio)

    # ──────────────────────────────────────────────
    # 2. Alle konfigurierten Companies auflisten
    # ──────────────────────────────────────────────
    print_section("2. Alle konfigurierten Companies auflisten")

    companies = multi_fio.list_companies()
    print(f"  Anzahl registrierter Companies: {len(companies)}")
    for code in companies:
        data = multi_fio.get_company_data(code)
        if data:
            print(f"    • {data.CompanyName} (Code: {code})")

    # ──────────────────────────────────────────────
    # 3. Demo-Daten für Planeten und Inventar laden
    # ──────────────────────────────────────────────
    print_section("3. Demo-Daten einspielen")

    # Planetendaten für MINER
    planeten_miner = [
        {
            "PlanetNaturalId": "UV-351a",
            "PlanetName": "Verdant Prime",
            "HasWarehouse": True,
            "HasLocalMarket": True,
        },
        {
            "PlanetNaturalId": "XK-590b",
            "PlanetName": "Iron Ridge",
            "HasWarehouse": False,
            "HasLocalMarket": False,
        },
    ]
    multi_fio.update_company_planets("MINER", planeten_miner)
    print("  ✓ Planeten für MINER gespeichert")

    # Planetendaten für TRADE
    planeten_trade = [
        {
            "PlanetNaturalId": "QT-114c",
            "PlanetName": "Nova Bazaar",
            "HasWarehouse": True,
            "HasLocalMarket": True,
        },
    ]
    multi_fio.update_company_planets("TRADE", planeten_trade)
    print("  ✓ Planeten für TRADE gespeichert")

    # Inventardaten für MINER
    inventar_miner = [
        {"MaterialTicker": "FE", "MaterialName": "Iron",
         "Quantity": 5000.0, "LocationName": "Verdant Prime"},
        {"MaterialTicker": "LST", "MaterialName": "Limestone",
         "Quantity": 2000.0, "LocationName": "Verdant Prime"},
        {"MaterialTicker": "H2O", "MaterialName": "Water",
         "Quantity": 800.0, "LocationName": "Iron Ridge"},
        {"MaterialTicker": "RAT", "MaterialName": "Rations",
         "Quantity": 300.0, "LocationName": "Iron Ridge"},
    ]
    multi_fio.update_company_inventory("MINER", inventar_miner)
    print("  ✓ Inventar für MINER gespeichert")

    # Inventardaten für TRADE
    inventar_trade = [
        {"MaterialTicker": "DW", "MaterialName": "Drinking Water",
         "Quantity": 10000.0, "LocationName": "Nova Bazaar"},
        {"MaterialTicker": "COF", "MaterialName": "Coffee",
         "Quantity": 1500.0, "LocationName": "Nova Bazaar"},
    ]
    multi_fio.update_company_inventory("TRADE", inventar_trade)
    print("  ✓ Inventar für TRADE gespeichert")

    # ──────────────────────────────────────────────
    # 4. Planeten für jede Company abrufen
    # ──────────────────────────────────────────────
    print_section("4. Planetenliste je Company")

    for code in companies:
        data = multi_fio.get_company_data(code)
        if data:
            print_section(f"{data.CompanyName} ({code})", level=2)
            demo_planeten_daten(multi_fio, code)

    # ──────────────────────────────────────────────
    # 5. Inventar für jede Company abrufen
    # ──────────────────────────────────────────────
    print_section("5. Inventar je Company")

    for code in companies:
        data = multi_fio.get_company_data(code)
        if data:
            print_section(f"{data.CompanyName} ({code})", level=2)
            demo_inventar_daten(multi_fio, code)

    # ──────────────────────────────────────────────
    # 6. Zusammenfassung
    # ──────────────────────────────────────────────
    print_header("Zusammenfassung", char="─")

    for code in companies:
        data = multi_fio.get_company_data(code)
        if data:
            print(f"\n  {data.CompanyName} ({code}):")
            print(f"    Planeten:        {len(data.Planets)}")
            print(f"    Inventar-Posten: {len(data.Inventory)}")
            total_qty = sum(item.Quantity for item in data.Inventory)
            print(f"    Gesamt-Menge:    {total_qty:.0f} Einheiten")

    print_header("Beispiel abgeschlossen ✓")


if __name__ == "__main__":
    main()
