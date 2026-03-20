"""Agent tools that wrap the services/ REST API via httpx."""

import os
import httpx
from langchain_core.tools import tool

SERVICES_API_URL = os.getenv("SERVICES_API_URL", "http://localhost:8000")


@tool
async def search_config(service_name: str, environment: str, config_key: str) -> str:
    """Search for a specific configuration by service name, environment, and key.
    Use this to check if a config exists before creating a new one."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SERVICES_API_URL}/api/configs/search",
            params={"service_name": service_name, "environment": environment, "config_key": config_key},
        )
    if resp.status_code == 404:
        return "Config not found."
    if resp.status_code != 200:
        return f"Error searching config: {resp.status_code} - {resp.text}"
    data = resp.json()
    return (
        f"Found config:\n"
        f"  ID: {data['id']}\n"
        f"  Service: {data['service_name']}\n"
        f"  Environment: {data['environment']}\n"
        f"  Key: {data['config_key']}\n"
        f"  Value: {data['config_value']}\n"
        f"  Description: {data['description']}\n"
        f"  Updated: {data['updated_at']}"
    )


@tool
async def create_config(
    service_name: str,
    environment: str,
    config_key: str,
    config_value: str,
    description: str = "",
) -> str:
    """Create a new configuration entry. Always search first to avoid duplicates."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SERVICES_API_URL}/api/configs",
            json={
                "service_name": service_name,
                "environment": environment,
                "config_key": config_key,
                "config_value": config_value,
                "description": description,
            },
        )
    if resp.status_code == 409:
        return f"Config already exists for {service_name}/{environment}/{config_key}. Use update instead."
    if resp.status_code == 201:
        data = resp.json()
        return f"Config created successfully (ID: {data['id']}): {service_name}/{environment}/{config_key} = {config_value}"
    return f"Error creating config: {resp.status_code} - {resp.text}"


@tool
async def list_configs(service_name: str = "", environment: str = "") -> str:
    """List configurations with optional filters by service name and/or environment."""
    params = {}
    if service_name:
        params["service_name"] = service_name
    if environment:
        params["environment"] = environment

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{SERVICES_API_URL}/api/configs", params=params)

    if resp.status_code != 200:
        return f"Error listing configs: {resp.status_code} - {resp.text}"

    configs = resp.json()
    if not configs:
        return "No configurations found matching the filters."

    lines = [f"Found {len(configs)} configuration(s):\n"]
    for c in configs:
        lines.append(f"  [{c['id']}] {c['service_name']}/{c['environment']}/{c['config_key']} = {c['config_value']}")
    return "\n".join(lines)


@tool
async def update_config(
    service_name: str, environment: str, config_key: str, new_value: str
) -> str:
    """Update an existing configuration's value. Searches for the config first."""
    async with httpx.AsyncClient() as client:
        # Find the config
        resp = await client.get(
            f"{SERVICES_API_URL}/api/configs/search",
            params={"service_name": service_name, "environment": environment, "config_key": config_key},
        )
        if resp.status_code == 404:
            return f"Config not found: {service_name}/{environment}/{config_key}"
        if resp.status_code != 200:
            return f"Error searching config: {resp.status_code} - {resp.text}"

        existing = resp.json()
        old_value = existing["config_value"]

        # Update it
        resp = await client.put(
            f"{SERVICES_API_URL}/api/configs/{existing['id']}",
            json={
                "service_name": service_name,
                "environment": environment,
                "config_key": config_key,
                "config_value": new_value,
                "description": existing["description"],
            },
        )
    if resp.status_code == 200:
        return f"Config updated: {service_name}/{environment}/{config_key} changed from '{old_value}' to '{new_value}'"
    return f"Error updating config: {resp.status_code} - {resp.text}"


@tool
async def delete_config(service_name: str, environment: str, config_key: str) -> str:
    """Delete a configuration entry. Searches for the config first."""
    async with httpx.AsyncClient() as client:
        # Find the config
        resp = await client.get(
            f"{SERVICES_API_URL}/api/configs/search",
            params={"service_name": service_name, "environment": environment, "config_key": config_key},
        )
        if resp.status_code == 404:
            return f"Config not found: {service_name}/{environment}/{config_key}"
        if resp.status_code != 200:
            return f"Error searching config: {resp.status_code} - {resp.text}"

        existing = resp.json()
        resp = await client.delete(f"{SERVICES_API_URL}/api/configs/{existing['id']}")

    if resp.status_code == 200:
        return f"Config deleted: {service_name}/{environment}/{config_key}"
    return f"Error deleting config: {resp.status_code} - {resp.text}"


# All tools exposed to the agent
all_tools = [search_config, create_config, list_configs, update_config, delete_config]
