import math

def compute_trajectories(aircraft_history):
    trajectories = []

    for states in aircraft_history.values():
        if not states:
            continue

        state = states[-1]
        required = (
            state.latitude,
            state.longitude,
            state.true_track,
            state.velocity,
        )
        if any(value is None for value in required):
            continue

        altitude_m = (
            state.geo_altitude
            if state.geo_altitude is not None
            else state.barometric_altitude
        )
        if altitude_m is None:
            continue

        vertical_rate_ms = state.vertical_rate or 0.0
        predicted_points = []

        for time_offset_s in range(0, 301, 30):
            latitude, longitude = predict_position(
                state.latitude,
                state.longitude,
                state.true_track,
                state.velocity,
                time_offset_s,
            )

            predicted_points.append({
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude_m + vertical_rate_ms * time_offset_s,
                "t_offset_s": time_offset_s,
            })

        callsign = (state.callsign or "").strip() or None
        trajectories.append({
            "icao24": state.icao24,
            "callsign": callsign,
            # Preserves compatibility with the current frontend.
            "positions": [
                [point["latitude"], point["longitude"]]
                for point in predicted_points
            ],
            "predicted_points": predicted_points,
        })

    return trajectories

def predict_position(lat, lon, heading_deg, speed_ms, t_seconds):
    """
    Predict the future position of an aircraft given its current position, heading, speed, and time offset.

    Parameters:
    lat (float): Current latitude in degrees.
    lon (float): Current longitude in degrees.
    heading_deg (float): Heading in degrees (0-360).
    speed_ms (float): Speed in meters per second.
    t_seconds (int): Time offset in seconds for prediction.

    Returns:
    tuple: Predicted latitude and longitude in degrees.
    """
    # Convert heading to radians
    heading_rad = math.radians(heading_deg)

    # Calculate distance traveled
    distance_m = speed_ms * t_seconds

    # Earth's radius in meters
    R = 6371000

    # Calculate new latitude
    new_lat = lat + (distance_m / R) * (180 / math.pi) * math.cos(heading_rad)

    # Calculate new longitude
    new_lon = lon + (distance_m / R) * (180 / math.pi) * math.sin(heading_rad) / math.cos(math.radians(lat))

    return new_lat, new_lon