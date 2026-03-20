"""CRUD endpoints for configuration management."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database import get_db
from ..models import ConfigCreate, ConfigResponse

router = APIRouter(prefix="/api/configs", tags=["configs"])


@router.get("/services")
async def list_services() -> list[str]:
    """List all distinct service names."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT DISTINCT service_name FROM configurations ORDER BY service_name")
        rows = await cursor.fetchall()
        return [row["service_name"] for row in rows]
    finally:
        await db.close()


@router.get("/environments")
async def list_environments() -> list[str]:
    """List all distinct environments."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT DISTINCT environment FROM configurations ORDER BY environment")
        rows = await cursor.fetchall()
        return [row["environment"] for row in rows]
    finally:
        await db.close()


@router.get("/search")
async def search_config(
    service_name: str = Query(...),
    environment: str = Query(...),
    config_key: str = Query(...),
) -> ConfigResponse:
    """Search for a config by exact match on service_name + environment + config_key."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM configurations WHERE service_name = ? AND environment = ? AND config_key = ?",
            (service_name, environment, config_key),
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Config not found")
        return ConfigResponse(**dict(row))
    finally:
        await db.close()


@router.get("/{config_id}")
async def get_config(config_id: int) -> ConfigResponse:
    """Get a single config by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM configurations WHERE id = ?", (config_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Config not found")
        return ConfigResponse(**dict(row))
    finally:
        await db.close()


@router.get("")
async def list_configs(
    service_name: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    config_key: Optional[str] = Query(None),
) -> list[ConfigResponse]:
    """List all configs with optional filters."""
    query = "SELECT * FROM configurations WHERE 1=1"
    params: list = []

    if service_name:
        query += " AND service_name = ?"
        params.append(service_name)
    if environment:
        query += " AND environment = ?"
        params.append(environment)
    if config_key:
        query += " AND config_key = ?"
        params.append(config_key)

    query += " ORDER BY service_name, environment, config_key"

    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [ConfigResponse(**dict(row)) for row in rows]
    finally:
        await db.close()


@router.post("", status_code=201)
async def create_config(config: ConfigCreate) -> ConfigResponse:
    """Create a new config. Returns 409 if a duplicate exists."""
    db = await get_db()
    try:
        # Check for duplicate
        cursor = await db.execute(
            "SELECT id FROM configurations WHERE service_name = ? AND environment = ? AND config_key = ?",
            (config.service_name, config.environment, config.config_key),
        )
        if await cursor.fetchone():
            raise HTTPException(
                status_code=409,
                detail=f"Config already exists for {config.service_name}/{config.environment}/{config.config_key}",
            )

        cursor = await db.execute(
            """INSERT INTO configurations (service_name, environment, config_key, config_value, description)
               VALUES (?, ?, ?, ?, ?)""",
            (config.service_name, config.environment, config.config_key, config.config_value, config.description),
        )
        await db.commit()

        # Fetch the created row
        cursor = await db.execute("SELECT * FROM configurations WHERE id = ?", (cursor.lastrowid,))
        row = await cursor.fetchone()
        return ConfigResponse(**dict(row))
    finally:
        await db.close()


@router.put("/{config_id}")
async def update_config(config_id: int, config: ConfigCreate) -> ConfigResponse:
    """Update an existing config by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id FROM configurations WHERE id = ?", (config_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Config not found")

        # Oracle equivalent: updated_at would use SYSTIMESTAMP
        await db.execute(
            """UPDATE configurations
               SET service_name = ?, environment = ?, config_key = ?, config_value = ?, description = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (config.service_name, config.environment, config.config_key, config.config_value, config.description, config_id),
        )
        await db.commit()

        cursor = await db.execute("SELECT * FROM configurations WHERE id = ?", (config_id,))
        row = await cursor.fetchone()
        return ConfigResponse(**dict(row))
    finally:
        await db.close()


@router.delete("/{config_id}")
async def delete_config(config_id: int) -> dict:
    """Delete a config by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id FROM configurations WHERE id = ?", (config_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Config not found")

        await db.execute("DELETE FROM configurations WHERE id = ?", (config_id,))
        await db.commit()
        return {"detail": "Config deleted successfully"}
    finally:
        await db.close()
