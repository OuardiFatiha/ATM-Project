import asyncio
from collections import deque, defaultdict

from app.fetcher import getAircraftStates
from app.models import AircraftState
from app.predictor import compute_trajectories
from fastapi import FastAPI
from python_opensky import BoundingBox

app = FastAPI()

# icao24 -> 10 derniers AircraftState
aircraft_history: dict[str, deque[AircraftState]] = defaultdict(lambda: deque(maxlen=10))
poller_task: asyncio.Task | None = None

# BBox fixe (zone surveillee)
TRACK_BBOX = BoundingBox(
    min_latitude=43.0,
    max_latitude=51.0,
    min_longitude=-1.0,
    max_longitude=8.0,
)

async def poll_aircraft_states():
    while True:
        try:
            states = await getAircraftStates(TRACK_BBOX)
            for s in states:
                if s.icao24:
                    aircraft_history[s.icao24].append(s)
        except Exception as e:
            print("poll error:", e)
            print(f"poll error type: {type(e).__name__}")
            print(f"poll error: {e!r}")
            print(f"underlying cause: {e.__cause__!r}")

        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    global poller_task
    poller_task = asyncio.create_task(poll_aircraft_states())

@app.on_event("shutdown")
async def shutdown_event():
    global poller_task
    if poller_task:
        poller_task.cancel()
        try:
            await poller_task
        except asyncio.CancelledError:
            pass


@app.get("/api")
async def read_root():
    return {"Hello": "World"}

@app.get("/api/aircraft/all")
async def read_aircraft(min_latitude: float, max_latitude: float, min_longitude: float, max_longitude: float):    
    return [states[-1] for states in aircraft_history.values() if states]

@app.get("/api/aircraft/trajectories")
async def read_aircraft_trajectories():
    return compute_trajectories(aircraft_history)
