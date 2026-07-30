import { Marker, Popup } from "react-leaflet";
import { aircraftIcon } from "../icons/aircraftIcon";

import type { AircraftState } from "../types/AircraftState";

export const AircraftDetail = ({ aircraft }: { aircraft: AircraftState }) => {
    if (aircraft.latitude === null || aircraft.longitude === null) {
        return null;
    }

    return (
        <Marker
            key={aircraft.icao24}
            position={{ lat: aircraft.latitude, lng: aircraft.longitude }}
            icon={aircraftIcon(aircraft.true_track ?? 0, aircraft.on_ground ? "green" : "purple")}
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
    );
}