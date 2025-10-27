import os
from typing import Optional, List
from contextlib import asynccontextmanager
import psycopg
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv


class DatabaseConfig:
    """Database configuration from environment variables"""
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "salesnisha")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.min_size = int(os.getenv("DB_POOL_MIN_SIZE", "10"))
        self.max_size = int(os.getenv("DB_POOL_MAX_SIZE", "20"))
        print(self.database)
    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class DatabaseRepository:
    """Database access repository with connection pooling using psycopg"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._pool: Optional[AsyncConnectionPool] = None
    
    async def connect(self):
        """Initialize database connection pool"""
        if self._pool is None:
            self._pool = AsyncConnectionPool(
                conninfo=self.config.connection_string,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                kwargs={"row_factory": dict_row}
            )
            await self._pool.open()
    
    async def disconnect(self):
        """Close database connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
    # Some changes
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self._pool:
            await self.connect()
        
        async with self._pool.connection() as conn:
            yield conn
    
    # Item operations
    async def get_item(self, itemid: str) -> Optional[dict]:
        """Get item by ID"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT itemid, name, description, unitofsale, created_at, updated_at FROM item WHERE itemid = %s",
                    (itemid,)
                )
                row = await cur.fetchone()
                return row if row else None
    
    async def get_all_items(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all items with pagination"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT itemid, name, description, unitofsale, created_at, updated_at FROM item ORDER BY itemid LIMIT %s OFFSET %s",
                    (limit, offset)
                )
                rows = await cur.fetchall()
                return rows
    
    async def insert_item(self, itemid: str, name: str, description: str, unitofsale: str) -> dict:
        """Insert a new item"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO item (itemid, name, description, unitofsale)
                    VALUES (%s, %s, %s, %s)
                    RETURNING itemid, name, description, unitofsale, created_at, updated_at
                    """,
                    (itemid, name, description, unitofsale)
                )
                row = await cur.fetchone()
                await conn.commit()
                return row
    
    async def update_item(self, itemid: str, name: str, description: str, unitofsale: str) -> Optional[dict]:
        """Update an existing item"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE item 
                    SET name = %s, description = %s, unitofsale = %s, updated_at = now()
                    WHERE itemid = %s
                    RETURNING itemid, name, description, unitofsale, created_at, updated_at
                    """,
                    (name, description, unitofsale, itemid)
                )
                row = await cur.fetchone()
                await conn.commit()
                return row if row else None
    
    async def upsert_item(self, itemid: str, name: str, description: str, unitofsale: str) -> dict:
        """Insert or update item (upsert)"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO item (itemid, name, description, unitofsale)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (itemid) DO UPDATE
                    SET name = EXCLUDED.name, 
                        description = EXCLUDED.description, 
                        unitofsale = EXCLUDED.unitofsale,
                        updated_at = now()
                    RETURNING itemid, name, description, unitofsale, created_at, updated_at
                    """,
                    (itemid, name, description, unitofsale)
                )
                row = await cur.fetchone()
                await conn.commit()
                return row
    
    async def delete_item(self, itemid: str) -> bool:
        """Delete an item"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM item WHERE itemid = %s", (itemid,))
                await conn.commit()
                return cur.rowcount == 1
    
    # Location operations
    async def get_location(self, locid: str) -> Optional[dict]:
        """Get location by ID"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT locid, name, description, address, contact, latitude, longitude,
                           storecategory, locationcategory, storecategorynote, locationcategorynote,
                           created_at, updated_at
                    FROM locations WHERE locid = %s
                    """,
                    (locid,)
                )
                row = await cur.fetchone()
                return row if row else None
    
    async def get_all_locations(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all locations with pagination"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT locid, name, description, address, contact, latitude, longitude,
                           storecategory, locationcategory, storecategorynote, locationcategorynote,
                           created_at, updated_at
                    FROM locations ORDER BY locid LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
                rows = await cur.fetchall()
                return rows
    
    async def insert_location(self, locid: str, name: str, description: str, address: str,
                            contact: str, latitude: str, longitude: str, storecategory: str,
                            locationcategory: str, storecategorynote: str, locationcategorynote: str) -> dict:
        """Insert a new location"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO locations (locid, name, description, address, contact, latitude, longitude,
                                         storecategory, locationcategory, storecategorynote, locationcategorynote)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING locid, name, description, address, contact, latitude, longitude,
                              storecategory, locationcategory, storecategorynote, locationcategorynote,
                              created_at, updated_at
                    """,
                    (locid, name, description, address, contact, latitude, longitude,
                     storecategory, locationcategory, storecategorynote, locationcategorynote)
                )
                row = await cur.fetchone()
                await conn.commit()
                return row
    
    async def upsert_location(self, locid: str, name: str, description: str, address: str,
                            contact: str, latitude: str, longitude: str, storecategory: str,
                            locationcategory: str, storecategorynote: str, locationcategorynote: str) -> dict:
        """Insert or update location (upsert)"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO locations (locid, name, description, address, contact, latitude, longitude,
                                         storecategory, locationcategory, storecategorynote, locationcategorynote)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (locid) DO UPDATE
                    SET name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        address = EXCLUDED.address,
                        contact = EXCLUDED.contact,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        storecategory = EXCLUDED.storecategory,
                        locationcategory = EXCLUDED.locationcategory,
                        storecategorynote = EXCLUDED.storecategorynote,
                        locationcategorynote = EXCLUDED.locationcategorynote,
                        updated_at = now()
                    RETURNING locid, name, description, address, contact, latitude, longitude,
                              storecategory, locationcategory, storecategorynote, locationcategorynote,
                              created_at, updated_at
                    """,
                    (locid, name, description, address, contact, latitude, longitude,
                     storecategory, locationcategory, storecategorynote, locationcategorynote)
                )
                row = await cur.fetchone()
                await conn.commit()
                return row
    
    async def delete_location(self, locid: str) -> bool:
        """Delete a location"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM locations WHERE locid = %s", (locid,))
                await conn.commit()
                return cur.rowcount == 1
    
    # Sale Event operations
    async def get_sale_event(self, event_id: int) -> Optional[dict]:
        """Get sale event by ID"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, locid, itemid, saleqty, year, month, day, hour, minute, second,
                           event_timezone, created_at
                    FROM sale_events WHERE id = %s
                    """,
                    (event_id,)
                )
                row = await cur.fetchone()
                return row if row else None
    
    async def get_sale_events(self, locid: Optional[str] = None, itemid: Optional[str] = None,
                            limit: int = 100, offset: int = 0) -> List[dict]:
        """Get sale events with optional filters"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT id, locid, itemid, saleqty, year, month, day, hour, minute, second,
                           event_timezone, created_at
                    FROM sale_events
                    WHERE 1=1
                """
                params = []
                
                if locid:
                    query += " AND locid = %s"
                    params.append(locid)
                
                if itemid:
                    query += " AND itemid = %s"
                    params.append(itemid)
                
                query += " ORDER BY id DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                await cur.execute(query, params)
                rows = await cur.fetchall()
                return rows
    
    async def insert_sale_event(self, locid: str, itemid: str, saleqty: float,
                               year: int, month: int, day: int, hour: int,
                               minute: int, second: int, event_timezone: str) -> dict:
        """Insert a new sale event"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO sale_events (locid, itemid, saleqty, year, month, day, hour, minute, second, event_timezone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, locid, itemid, saleqty, year, month, day, hour, minute, second, event_timezone, created_at
                    """,
                    (locid, itemid, saleqty, year, month, day, hour, minute, second, event_timezone)
                )
                row = await cur.fetchone()
                await conn.commit()
                return row
    
    async def bulk_insert_sale_events(self, events: List[tuple]) -> int:
        """Bulk insert sale events for performance"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(
                    """
                    INSERT INTO sale_events (locid, itemid, saleqty, year, month, day, hour, minute, second, event_timezone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    events
                )
                await conn.commit()
                return len(events)
    
    async def get_sales_by_date_range(self, start_year: int, start_month: int, start_day: int,
                                     end_year: int, end_month: int, end_day: int,
                                     locid: Optional[str] = None, itemid: Optional[str] = None) -> List[dict]:
        """Get sale events within a date range"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT id, locid, itemid, saleqty, year, month, day, hour, minute, second,
                           event_timezone, created_at
                    FROM sale_events
                    WHERE (year > %s OR (year = %s AND month > %s) OR (year = %s AND month = %s AND day >= %s))
                      AND (year < %s OR (year = %s AND month < %s) OR (year = %s AND month = %s AND day <= %s))
                """
                params = [start_year, start_year, start_month, start_year, start_month, start_day,
                         end_year, end_year, end_month, end_year, end_month, end_day]
                
                if locid:
                    query += " AND locid = %s"
                    params.append(locid)
                
                if itemid:
                    query += " AND itemid = %s"
                    params.append(itemid)
                
                query += " ORDER BY year, month, day, hour, minute, second"
                
                await cur.execute(query, params)
                rows = await cur.fetchall()
                return rows
    
    # Health check
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    return True
        except Exception:
            return False

# Global repository instance
db_repo: Optional[DatabaseRepository] = None

def get_db_repo() -> DatabaseRepository:
    """Get the global database repository instance"""
    global db_repo
    if db_repo is None:
        db_repo = DatabaseRepository()
    return db_repo