import { useAircraftStates } from "../hooks/useAircraftStates";
import { AircraftDetail } from "./AircraftDetail";

export const AircraftList = () => {
    const { aircraftStates } = useAircraftStates();

    return (
        <>
            {aircraftStates && aircraftStates.map((aircraft) => {
                return (
                    <AircraftDetail key={aircraft.icao24} aircraft={aircraft} />
                );
            })}
        </>
    );
};