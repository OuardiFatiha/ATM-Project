import { useAircraftStates } from "../hooks/useAircraftStates";
import { AircraftDetail } from "./AircraftDetail";
import { useTrajectories } from "../hooks/useTrajectories";
import { useMemo } from "react";

export const AircraftList = () => {
    const { aircraftStates } = useAircraftStates();
    const { trajectories } = useTrajectories();

    const trajectory = useMemo(() => {
        return (icao24: string) => {
            return trajectories.find((trajectory) => trajectory.icao24 === icao24);
        };
    }, [trajectories]);

    return (
        <>
            {aircraftStates && trajectories && aircraftStates.map((aircraft) => {
                return (
                    <AircraftDetail key={aircraft.icao24} aircraft={aircraft} trajectory={trajectory(aircraft.icao24)} />
                );
            })}
        </>
    );
};