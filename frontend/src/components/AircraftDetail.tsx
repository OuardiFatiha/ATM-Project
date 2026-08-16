import { Marker, Popup } from "react-leaflet";
import { aircraftIcon } from "../icons/aircraftIcon";

import type { AircraftState } from "../types/AircraftState";
import type { Trajectory } from "../types/Trajectory";
import { useMemo } from "react";
import { AircraftTrajectory } from "./AircraftTrajectory";

interface AircraftDetailProps {
    aircraft: AircraftState;
    trajectory?: Trajectory;
}

export const AircraftDetail = ({ aircraft, trajectory }: AircraftDetailProps) => {


    const aircraftColor = useMemo(() => {
        return (): string => {
            const heading = ((aircraft.true_track ?? 0) % 360 + 360) % 360;
            return `hsl(${heading}, 75%, 45%)`;
        };
    }, [aircraft.true_track]);

    if (aircraft.latitude === null || aircraft.longitude === null) {
        return null;
    }

    return (
        <>
            <Marker
                key={aircraft.icao24}
                position={{ lat: aircraft.latitude, lng: aircraft.longitude }}
                icon={aircraftIcon(
                    aircraft.true_track ?? 0,
                    aircraft.on_ground ? "#6b7280" : aircraftColor(),
                )}
                eventHandlers={{
                    mouseover(e) {
                        e.target.openPopup();
                    },
                    mouseout(e) {
                        e.target.closePopup();
                    },
                    click: () => console.log(`Clicked on aircraft: ${aircraft.icao24}`)
                }}
            >
                <Popup>
                    <div>
                        <p><strong>{aircraft.callsign || aircraft.icao24}</strong></p>
                        <p>Country: {aircraft.origin_country}</p>
                        <p>Altitude: {aircraft.barometric_altitude}m</p>
                        <p>Velocity: {aircraft.velocity} m/s</p>
                        <p>Status: {aircraft.on_ground ? "On Ground" : "In Air"}</p>
                    </div>
                </Popup>
            </Marker>
            {trajectory && <AircraftTrajectory trajectory={trajectory} color={aircraftColor()} />}
        </>
    );
};