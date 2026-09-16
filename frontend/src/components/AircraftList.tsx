import { useAircraftStates } from "../hooks/useAircraftStates";
import { AircraftDetail } from "./AircraftDetail";
import { useTrajectories } from "../hooks/useTrajectories";
import { useEffect, useMemo, useRef } from "react";
import { Toast } from "primereact/toast";

export const AircraftList = () => {
    const { aircraftStates, error } = useAircraftStates();
    const { trajectories } = useTrajectories();
    const toast = useRef<Toast>(null);


    const trajectory = useMemo(() => {
        return (icao24: string) => {
            return trajectories.find((trajectory) => trajectory.icao24 === icao24);
        };
    }, [trajectories]);

    useEffect(() => {
        if (error) {
            toast.current?.show({
                severity: "error",
                summary: "Error",
                detail: error,
            });
        }
    }, [error]);

    return (
        <>
            <Toast ref={toast} position="bottom-right" />
            {aircraftStates && trajectories && aircraftStates.map((aircraft) => {
                return (
                    <AircraftDetail key={aircraft.icao24} aircraft={aircraft} trajectory={trajectory(aircraft.icao24)} />
                );
            })}
        </>
    );
};