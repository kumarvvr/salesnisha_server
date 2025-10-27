
-- Table for Sale Events
CREATE TABLE sale_events (
    id BIGSERIAL PRIMARY KEY,
    locid TEXT NOT NULL DEFAULT '',
    itemid TEXT NOT NULL DEFAULT '',
    saleqty REAL NOT NULL DEFAULT 0.0,
    year INTEGER NOT NULL DEFAULT 0,
    month SMALLINT NOT NULL DEFAULT 0,
    day SMALLINT NOT NULL DEFAULT 0,
    hour SMALLINT NOT NULL DEFAULT 0,
    minute SMALLINT NOT NULL DEFAULT 0,
    second SMALLINT NOT NULL DEFAULT 0,
    event_timezone TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX idx_sale_events_locid ON sale_event(locid);
CREATE INDEX idx_sale_events_itemid ON sale_event(itemid);
CREATE INDEX idx_sale_events_date ON sale_event(year, month, day);

-- Table for item details
CREATE TABLE item (
    itemid TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    unitofsale TEXT NOT NULL DEFAULT 'ea',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for name lookups
CREATE INDEX idx_item_name ON item(name);

-- Table for Locations
CREATE TABLE locations (
    locid TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    contact TEXT NOT NULL DEFAULT '',
    latitude TEXT NOT NULL DEFAULT '',
    longitude TEXT NOT NULL DEFAULT '',
    storecategory TEXT NOT NULL DEFAULT 'retail',
    locationcategory TEXT NOT NULL DEFAULT 'store',
    storecategorynote TEXT NOT NULL DEFAULT '',
    locationcategorynote TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX idx_locations_name ON locations(name);
CREATE INDEX idx_locations_storecategory ON locations(storecategory);
CREATE INDEX idx_locations_locationcategory ON locations(locationcategory);
CREATE INDEX idx_locations_lat_lng ON locations(latitude, longitude);