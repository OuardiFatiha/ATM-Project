from math import radians, sin, cos, sqrt, atan2

from itertools import combinations
from datetime import datetime, timezone


METERS_TO_FEET = 3.28084

def detect_conflicts(
    trajectories,
    horizontal_threshold_nm=5.0,
    vertical_threshold_ft=1000.0,
):
    conflicts = []

    for trajectory_1, trajectory_2 in combinations(trajectories, 2):
        points_1 = {
            point["t_offset_s"]: point
            for point in trajectory_1["predicted_points"]
        }
        points_2 = {
            point["t_offset_s"]: point
            for point in trajectory_2["predicted_points"]
        }

        # Compare only points predicted for the same future instant.
        shared_offsets = sorted(points_1.keys() & points_2.keys())

        for offset in shared_offsets:
            point_1 = points_1[offset]
            point_2 = points_2[offset]

            horizontal_nm = haversine_nm(
                point_1["latitude"],
                point_1["longitude"],
                point_2["latitude"],
                point_2["longitude"],
            )
            vertical_ft = (
                abs(point_1["altitude"] - point_2["altitude"])
                * METERS_TO_FEET
            )

            if (
                horizontal_nm < horizontal_threshold_nm
                and vertical_ft < vertical_threshold_ft
            ):
                conflicts.append({
                    "icao24_1": trajectory_1["icao24"],
                    "icao24_2": trajectory_2["icao24"],
                    "callsign_1": trajectory_1["callsign"],
                    "callsign_2": trajectory_2["callsign"],
                    "time_to_conflict_s": offset,
                    "horizontal_dist_nm": horizontal_nm,
                    "vertical_dist_ft": vertical_ft,
                    "severity": (
                        "critical"
                        if horizontal_nm < 3 and vertical_ft < 500
                        else "warning"
                    ),
                    "detected_at": datetime.now(timezone.utc),
                })

                # Return the earliest predicted conflict for this pair.
                break

    return conflicts

def haversine_nm(lat1, lon1, lat2, lon2):
    R = 3440.065  # Radius of the Earth in nautical miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c