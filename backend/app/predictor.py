import math

def compute_trajectories(aircraft_history):
    """
    Compute the predicted trajectories for all aircraft in the aircraft_history.

    Returns:
    list: A list of lists of predicted positions.
    """
    trajectories = []
    last_states = [states[-1] for states in aircraft_history.values() if states]
    for last_state in last_states:
        if last_state:
            predicted_positions = [[last_state.latitude, last_state.longitude]]  # Start with the last known position
            for t in range(1, 11):  # Predict for the next 30, 60, ..., 300 seconds (10 steps)
                predicted_lat, predicted_lon = predict_position(
                    last_state.latitude,
                    last_state.longitude,
                    last_state.true_track,
                    last_state.velocity,
                    t * 30
                )
                predicted_positions.append([predicted_lat, predicted_lon])
            trajectories.append(predicted_positions)
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