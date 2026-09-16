import asyncio
import os
import aiohttp
from collections import deque, defaultdict

from app.fetcher import getAircraftStates
from app.models import AircraftState
from app.predictor import compute_trajectories
from app.opensky_auth import OpenSkyTokenManager
from fastapi import FastAPI, HTTPException

app = FastAPI()

# icao24 -> 10 derniers AircraftState
aircraft_history: dict[str, deque[AircraftState]] = defaultdict(lambda: deque(maxlen=10))
poller_task: asyncio.Task | None = None
http_session: aiohttp.ClientSession | None = None
token_manager: OpenSkyTokenManager | None = None
rate_limited_until: float | None = None  # monotonic timestamp

# BBox fixe (zone surveillee)
TRACK_BBOX = {
    "min_latitude": 43.0,
    "max_latitude": 51.0,
    "min_longitude": -1.0,
    "max_longitude": 8.0,
}

async def poll_aircraft_states():
    global rate_limited_until
    while True:
        try:
            states = await getAircraftStates(http_session, token_manager, TRACK_BBOX)
            for s in states:
                if s.icao24:
                    aircraft_history[s.icao24].append(s)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                retry_after = int(e.headers.get("X-Rate-Limit-Retry-After-Seconds", 60))
                rate_limited_until = asyncio.get_event_loop().time() + retry_after
                print(f"rate limited, backing off {retry_after}s")
                await asyncio.sleep(retry_after)
                continue
            print("poll error:", e)
        except Exception as e:
            print("poll error:", e)
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    global poller_task, http_session, token_manager
    # Configure the connector to skip SSL validation globally for this session
    connector = aiohttp.TCPConnector(ssl=False)
    http_session = aiohttp.ClientSession(connector=connector)
    token_manager = OpenSkyTokenManager(
        os.environ["OPENSKY_CLIENT_ID"],
        os.environ["OPENSKY_CLIENT_SECRET"],
    )
    poller_task = asyncio.create_task(poll_aircraft_states())

@app.on_event("shutdown")
async def shutdown_event():
    global poller_task, http_session
    if poller_task:
        poller_task.cancel()
        try:
            await poller_task
        except asyncio.CancelledError:
            pass
    if http_session:
        await http_session.close()


@app.get("/api")
async def read_root():
    return {"Hello": "World"}

@app.get("/api/aircraft/all")
async def read_aircraft(): 
    if rate_limited_until and asyncio.get_event_loop().time() < rate_limited_until:
            raise HTTPException(status_code=429, detail="OpenSky rate limit exceeded, try again later")  
    return [states[-1] for states in aircraft_history.values() if states]

@app.get("/api/aircraft/trajectories")
async def read_aircraft_trajectories():
    return compute_trajectories(aircraft_history)
