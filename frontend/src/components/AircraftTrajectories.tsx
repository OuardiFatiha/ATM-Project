import { Polyline } from "react-leaflet";
import { useTrajectories } from "../hooks/useTrajectories";


export const AircraftTrajectories = () => {
    const { trajectories } = useTrajectories();

    return (
        <Polyline pathOptions={{ color: "cyan", dashArray: "3, 5", weight: 2 }} positions={trajectories} />
    );
};