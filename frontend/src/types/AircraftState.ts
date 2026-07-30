export type AircraftState = {
  icao24: string;
  callsign: string | null;
  origin_country: string;
  time_position: string | null;
  last_contact: string | null;
  longitude: number | null;
  latitude: number | null;
  barometric_altitude: number | null;
  on_ground: boolean;
  velocity: number | null;
  true_track: number | null;
  vertical_rate: number | null;
  sensors: number[] | null;
  geo_altitude: number | null;
  position_source: number | null;
};