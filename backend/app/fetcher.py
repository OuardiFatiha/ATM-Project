import aiohttp
from app.models import AircraftState
from app.opensky_auth import OpenSkyTokenManager

STATES_URL = "https://opensky-network.org/api/states/all"

async def getAircraftStates(session: aiohttp.ClientSession, tokens: OpenSkyTokenManager, bbox):
    token = await tokens.get_token(session)
    params = {
        "lamin": bbox["min_latitude"],
        "lamax": bbox["max_latitude"],
        "lomin": bbox["min_longitude"],
        "lomax": bbox["max_longitude"],
        "extended": 1,
    }
    async with session.get(
        STATES_URL,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        ssl=False,
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
    return parseAircraftStates(data.get("states") or [])

def parseAircraftStates(states: list):
    keys = [
        "icao24", "callsign", "origin_country", "time_position", "last_contact",
        "longitude", "latitude", "barometric_altitude", "on_ground", "velocity",
        "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
        "spi", "position_source", "category",
    ]
    return [
        AircraftState.model_validate(dict(zip(keys, state)), from_attributes=True)
        for state in states
    ]
