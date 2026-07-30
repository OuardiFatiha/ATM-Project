from app.models import AircraftState
from python_opensky import OpenSky, BoundingBox, StatesResponse

async def getAircraftStates(bbox: BoundingBox):
    api = OpenSky()
    # bbox = (min latitude, max latitude, min longitude, max longitude)
    states: StatesResponse = await api.get_states(bounding_box=bbox)
    aircraft_states_list = parseAircraftStates(states)
    return aircraft_states_list

def parseAircraftStates(states: StatesResponse):
    aircraft_states_list = []
    print("number of states:", len(states.states))
    for state in states.states:
        state = AircraftState.model_validate(state, from_attributes=True)
        print("Here", repr(state))
        aircraft_states_list.append(state)
    return aircraft_states_list
