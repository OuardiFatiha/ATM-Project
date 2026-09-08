import asyncio
import os
import aiohttp
from collections import deque, defaultdict

from app.fetcher import getAircraftStates
from app.models import AircraftState
from app.predictor import compute_trajectories
from app.opensky_auth import OpenSkyTokenManager
from fastapi import FastAPI

app = FastAPI()

# icao24 -> 10 derniers AircraftState
aircraft_history: dict[str, deque[AircraftState]] = defaultdict(lambda: deque(maxlen=10))
poller_task: asyncio.Task | None = None
http_session: aiohttp.ClientSession | None = None
token_manager: OpenSkyTokenManager | None = None
# BBox fixe (zone surveillee)
TRACK_BBOX = {
    "min_latitude": 43.0,
    "max_latitude": 51.0,
    "min_longitude": -1.0,
    "max_longitude": 8.0,
}

async def poll_aircraft_states():
    while True:
        try:
            states = await getAircraftStates(http_session, token_manager, TRACK_BBOX)
            for s in states:
                if s.icao24:
                    aircraft_history[s.icao24].append(s)
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
    return [states[-1] for states in aircraft_history.values() if states]

@app.get("/api/aircraft/trajectories")
async def read_aircraft_trajectories():
    return compute_trajectories(aircraft_history)
