from pydantic import BaseModel

class SaleEvent(BaseModel):
    locid:str = ""
    itemid:str=""
    saleqty:float = 0.0
    year:int = 0
    month:int = 0
    day:int = 0
    hour:int = 0
    minute:int = 0
    second:int = 0
    event_timezone:str = ""

class Item(BaseModel):
    itemid:str = ""
    name:str = ""
    description:str =""
    unitofsale:str = "ea"

class Location(BaseModel):
    locid:str=""
    name:str = ""
    description:str= ""
    address:str = ""
    contact:str = ""
    latitude:str = ""
    longitude:str=""
    storecategory:str = "retail" # Warehouse, Kiosk, Event, Exhibition, etc
    locationcategory:str = "store" # Mall, Event, Festival, Etc
    storecategorynote:str = ""
    locationcategorynote:str = ""