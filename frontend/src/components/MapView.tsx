import { useEffect, useState } from "react"
import { useMapEvents } from "react-leaflet/hooks"
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet"
import { useMap } from "react-leaflet/hooks"
import type { LatLng, LocationEvent } from "leaflet"
import { useAircraftStates } from "../hooks/useAircraftStates"
import { aircraftIcon } from "../icons/aircraftIcon"

function LocationMarker() {
  const [position, setPosition] = useState<LatLng | null>(null)
  const map = useMapEvents({
    click() {
      map.locate()
    },
    locationfound(e: LocationEvent) {
      setPosition(e.latlng)
      map.flyTo(e.latlng, map.getZoom())
    },
  })

  return position === null ? null : (
    <Marker position={position}>
      <Popup>You are here</Popup>
    </Marker>
  )
}

function MapResizeFix() {
  const map = useMap()

  useEffect(() => {
    const refreshSize = () => map.invalidateSize()

    refreshSize()
    window.addEventListener("resize", refreshSize)

    return () => window.removeEventListener("resize", refreshSize)
  }, [map])

  return null
}

export const MapView = () => {
  const { aircraftStates } = useAircraftStates();

  return (
    <MapContainer
      center={{ lat: 48.86, lng: 2.28 }}
      zoom={10}
      scrollWheelZoom={false}
      style={{ width: "100%", height: "100%", overflow: "hidden" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapResizeFix />
      <LocationMarker />
      {aircraftStates && aircraftStates.map((aircraft) => {
        if (aircraft.latitude !== null && aircraft.longitude !== null) {
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
        return null;
      })}
    </MapContainer>
  );
};
