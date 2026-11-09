import asyncio
import os
import aiohttp
from collections import deque, defaultdict
from fastapi import FastAPI, HTTPException, WebSocket
from contextlib import asynccontextmanager

from fastapi.encoders import jsonable_encoder

from app.fetcher import getAircraftStates
from app.models import AircraftState
from app.predictor import compute_trajectories
from app.opensky_auth import OpenSkyTokenManager
from app.conflict import detect_conflicts

app = FastAPI()

# icao24 -> 10 derniers AircraftState
aircraft_history: dict[str, deque[AircraftState]] = defaultdict(lambda: deque(maxlen=10))
poller_task: asyncio.Task | None = None
http_session: aiohttp.ClientSession | None = None
token_manager: OpenSkyTokenManager | None = None
rate_limited_until: float | None = None  # monotonic timestamp
latest_trajectories = []
latest_conflicts = []

# BBox fixe (zone surveillee)
TRACK_BBOX = {
    "min_latitude": 43.0,
    "max_latitude": 51.0,
    "min_longitude": -1.0,
    "max_longitude": 8.0,
}

# WebSocket condition and version for live updates
version = 0
snapshot_cond = asyncio.Condition()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global poller_task, http_session, token_manager
    connector = aiohttp.TCPConnector(ssl=False)
    http_session = aiohttp.ClientSession(connector=connector)
    token_manager = OpenSkyTokenManager(
        os.environ["OPENSKY_CLIENT_ID"],
        os.environ["OPENSKY_CLIENT_SECRET"],
    )
    poller_task = asyncio.create_task(poll_aircraft_states(http_session, token_manager))

    yield  # l'application sert les requêtes ici

    if poller_task:
        poller_task.cancel()
        try:
            await poller_task
        except asyncio.CancelledError:
            pass
    if http_session:
        await http_session.close()

app = FastAPI(lifespan=lifespan)

async def poll_aircraft_states(session: aiohttp.ClientSession, tokens: OpenSkyTokenManager):
    global rate_limited_until, version
    while True:
        try:
            states = await getAircraftStates(
                session,
                tokens,
                TRACK_BBOX,
            )

            for state in states:
                if state.icao24:
                    aircraft_history[state.icao24].append(state)

            # Un seul calcul à chaque actualisation OpenSky.
            trajectories = compute_trajectories(aircraft_history)
            conflicts = detect_conflicts(trajectories)

            # Remplacement atomique des snapshots.
            async with snapshot_cond:
                latest_trajectories[:] = trajectories
                latest_conflicts[:] = conflicts
                version += 1
                snapshot_cond.notify_all()

        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                headers = e.headers or {}
                retry_after = int(headers.get("X-Rate-Limit-Retry-After-Seconds", 60))
                rate_limited_until = asyncio.get_event_loop().time() + retry_after
                print(f"rate limited, backing off {retry_after}s")
                await asyncio.sleep(retry_after)
                continue
            print("poll error:", e)
        except Exception as e:
            print("poll error:", e)
        await asyncio.sleep(10)

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
    return latest_trajectories

@app.get("/api/aircraft/conflicts")
async def read_aircraft_conflicts():
    return latest_conflicts

@app.websocket("/ws/live")
async def live(ws: WebSocket):
    await ws.accept()
    last_sent = -1
    while True:
        async with snapshot_cond:
            await snapshot_cond.wait_for(lambda: version != last_sent)
            current = version
        await ws.send_json(jsonable_encoder({
            "states": [states[-1] for states in aircraft_history.values() if states],
            "trajectories": latest_trajectories,
            "conflicts": latest_conflicts,
        }))
        last_sent = current