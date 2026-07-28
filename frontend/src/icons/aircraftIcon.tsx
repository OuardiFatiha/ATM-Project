import L from "leaflet"

export const aircraftIcon = (heading: number, color: string) =>
  L.divIcon({
    className: "aircraft-marker",
    html: `
      <div style="transform: rotate(${heading}deg); width: 24px; height: 24px;">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="${color}">
          <path d="M11 2l2 0 1 7 6 3 0 2-6-1-1 8-2 0-1-8-6 1 0-2 6-3z"/>
        </svg>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  })
