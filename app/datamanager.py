import json
import os
from typing import List, Dict
from datacontext import get_db_repo
from models import Item, Location

def load_items_from_json(file_path: str = "items.json") -> List[Item]:
    """Load items from JSON file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Items file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = []
    for item_data in data.get("items", []):
        items.append(Item(**item_data))
    
    return items

def load_locations_from_json(file_path: str = "locations.json") -> List[Location]:
    """Load locations from JSON file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Locations file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    locations = []
    for loc_data in data.get("locations", []):
        locations.append(Location(**loc_data))
    
    return locations

async def UpdateItems(file_path: str = "items.json") -> Dict[str, int]:
    """
    Iterate through the items in "items.json"
    check insert / update item in the database.
    Returns dict with counts of inserted/updated items.
    """
    db = get_db_repo()
    await db.connect()
    
    items = await load_items_from_json(file_path)
    
    inserted = 0
    updated = 0
    errors = 0
    
    for item in items:
        try:
            # Check if item exists
            existing = await db.get_item(item.itemid)
            
            if existing:
                # Update existing item
                await db.update_item(
                    itemid=item.itemid,
                    name=item.name,
                    description=item.description,
                    unitofsale=item.unitofsale
                )
                updated += 1
            else:
                # Insert new item
                await db.insert_item(
                    itemid=item.itemid,
                    name=item.name,
                    description=item.description,
                    unitofsale=item.unitofsale
                )
                inserted += 1
        except Exception as e:
            print(f"Error processing item {item.itemid}: {e}")
            errors += 1
    
    return {
        "total": len(items),
        "inserted": inserted,
        "updated": updated,
        "errors": errors
    }

async def UpdateLocations(file_path: str = "app/locations.json") -> Dict[str, int]:
    """
    Iterate through the locations in "locations.json"
    check insert / update location in the database.
    Returns dict with counts of inserted/updated locations.
    """
    db = get_db_repo()
    await db.connect()
    
    locations = await load_locations_from_json(file_path)
    
    inserted = 0
    updated = 0
    errors = 0
    
    for loc in locations:
        try:
            # Use upsert for simpler code
            await db.upsert_location(
                locid=loc.locid,
                name=loc.name,
                description=loc.description,
                address=loc.address,
                contact=loc.contact,
                latitude=loc.latitude,
                longitude=loc.longitude,
                storecategory=loc.storecategory,
                locationcategory=loc.locationcategory,
                storecategorynote=loc.storecategorynote,
                locationcategorynote=loc.locationcategorynote
            )
            
            # Check if it was an insert or update by querying created_at vs updated_at
            location_data = await db.get_location(loc.locid)
            if location_data and location_data['created_at'] == location_data['updated_at']:
                inserted += 1
            else:
                updated += 1
                
        except Exception as e:
            print(f"Error processing location {loc.locid}: {e}")
            errors += 1
    
    return {
        "total": len(locations),
        "inserted": inserted,
        "updated": updated,
        "errors": errors
    }