import { Polyline } from "react-leaflet";
import type { Trajectory } from "../types/Trajectory";

interface AircraftTrajectoryProps {
    trajectory: Trajectory;
    color?: string;
}

export const AircraftTrajectory = ({ trajectory, color = "cyan" }: AircraftTrajectoryProps) => {
    return (
        <Polyline pathOptions={{ color: color ?? "cyan", dashArray: "3, 5", weight: 2 }} positions={trajectory.positions} />
    );
};