"""Seed script to populate the database with sample configuration data."""

import asyncio
from database import get_db, init_db

SEED_DATA = [
    # auth-service
    ("auth-service", "dev", "db_timeout", "5000", "Database connection timeout in ms"),
    ("auth-service", "dev", "log_level", "debug", "Application log level"),
    ("auth-service", "dev", "max_retries", "3", "Max retry attempts for failed operations"),
    ("auth-service", "staging", "db_timeout", "3000", "Database connection timeout in ms"),
    ("auth-service", "staging", "log_level", "info", "Application log level"),
    ("auth-service", "prod", "db_timeout", "2000", "Database connection timeout in ms"),
    ("auth-service", "prod", "log_level", "warn", "Application log level"),
    ("auth-service", "prod", "max_retries", "5", "Max retry attempts for failed operations"),
    # payment-service
    ("payment-service", "dev", "api_rate_limit", "100", "API requests per minute per client"),
    ("payment-service", "dev", "cache_ttl", "300", "Cache time-to-live in seconds"),
    ("payment-service", "staging", "api_rate_limit", "500", "API requests per minute per client"),
    ("payment-service", "staging", "cache_ttl", "600", "Cache time-to-live in seconds"),
    ("payment-service", "prod", "api_rate_limit", "1000", "API requests per minute per client"),
    # order-service
    ("order-service", "dev", "batch_size", "50", "Order processing batch size"),
    ("order-service", "prod", "batch_size", "200", "Order processing batch size"),
    ("order-service", "prod", "cache_ttl", "900", "Cache time-to-live in seconds"),
]


async def seed():
    """Insert sample configs, skipping any that already exist."""
    await init_db()
    db = await get_db()
    try:
        for service_name, env, key, value, desc in SEED_DATA:
            # Skip if already exists (idempotent seed)
            cursor = await db.execute(
                "SELECT id FROM configurations WHERE service_name = ? AND environment = ? AND config_key = ?",
                (service_name, env, key),
            )
            if await cursor.fetchone():
                continue
            await db.execute(
                "INSERT INTO configurations (service_name, environment, config_key, config_value, description) VALUES (?, ?, ?, ?, ?)",
                (service_name, env, key, value, desc),
            )
        await db.commit()
        print(f"Seeded {len(SEED_DATA)} configurations.")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(seed())
