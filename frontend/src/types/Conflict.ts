export type Conflict = {
    icao24_1: string;
    icao24_2: string;
    callsign_1: string | null;
    callsign_2: string | null;
    time_to_conflict_s: number;
    horizontal_dist_nm: number;
    vertical_dist_ft: number;
    severity: 'warning' | 'critical';
    detected_at: string;
};
