import { useEffect, useState } from "react"
import { useMapEvents } from "react-leaflet/hooks"
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet"
import { useMap } from "react-leaflet/hooks"
import type { LatLng, LocationEvent } from "leaflet"
import { AircraftList } from "./AircraftList"

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
  return (
    <MapContainer
      center={{ lat: 48.86, lng: 2.28 }}
      zoom={10}
      scrollWheelZoom={true}
      style={{ width: "100%", height: "100%", overflow: "hidden" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapResizeFix />
      <LocationMarker />
      <AircraftList />
    </MapContainer>
  );
};
