# services/temperature_service.py
import asyncio
import httpx
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from city_CRUD import models
from .models import Temperature
from city_CRUD.models import City

API_KEY = "YourAPIToken"
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


async def fetch_coordinates(client: httpx.AsyncClient, city_name: str):
    """Fetch lat/lon for a given city name."""
    params = {"q": city_name, "limit": 1, "appid": API_KEY}
    r = await client.get(GEOCODE_URL, params=params)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None, None
    lat, lon = data[0]["lat"], data[0]["lon"]
    return lat, lon


async def fetch_temperature(client: httpx.AsyncClient, lat: float, lon: float):
    """Fetch current temperature for coordinates."""
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    r = await client.get(WEATHER_URL, params=params)
    r.raise_for_status()
    data = r.json()
    return data["main"]["temp"]


async def update_all_temperatures(session: AsyncSession):
    """Fetch temperatures for all cities and update or create records."""
    result = await session.execute(select(City))
    cities = result.scalars().all()

    async with httpx.AsyncClient() as client:
        for city in cities:
            lat, lon = await fetch_coordinates(client, city.name)
            if lat is None or lon is None:
                print(f"⚠️ Could not fetch coordinates for {city.name}")
                continue

            temp = await fetch_temperature(client, lat, lon)

            result = await session.execute(select(Temperature).where(Temperature.city_id == city.id))
            existing_entry = result.scalar_one_or_none()

            if existing_entry:
                existing_entry.temperature = temp
                existing_entry.date_time = datetime.utcnow()
                print(f"🔁 Updated {city.name} temperature to {temp}°C.")
            else:
                new_entry = Temperature(
                    city_id=city.id,
                    temperature=temp,
                    date_time=datetime.utcnow()
                )
                session.add(new_entry)
                print(f"🌡️ Added new temperature record for {city.name}: {temp}°C.")

        await session.commit()
        print("✅ All city temperatures updated.")
