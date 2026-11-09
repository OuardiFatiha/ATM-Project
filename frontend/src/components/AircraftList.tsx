import { AircraftDetail } from "./AircraftDetail";
import { useEffect, useMemo, useRef } from "react";
import { Toast } from "primereact/toast";
import { useLiveFeedContext } from "../context/LiveFeedContext";

export const AircraftList = () => {
    const { liveSnapshot, error } = useLiveFeedContext();
    const aircraftStates = liveSnapshot?.states ?? [];
    const trajectories = useMemo(() => liveSnapshot?.trajectories ?? [], [liveSnapshot?.trajectories]);
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