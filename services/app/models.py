"""Pydantic models for configuration entries."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class ConfigCreate(BaseModel):
    """Request model for creating/updating a configuration."""
    service_name: str
    environment: Literal["dev", "staging", "prod"]
    config_key: str
    config_value: str
    description: str = ""


class ConfigResponse(ConfigCreate):
    """Response model including DB-generated fields."""
    id: int
    created_at: datetime
    updated_at: datetime
