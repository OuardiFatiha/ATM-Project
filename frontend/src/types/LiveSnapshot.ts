import type { Trajectory } from "./Trajectory";
import type { Conflict } from "./Conflict";
import type { AircraftState } from "./AircraftState";

export type LiveSnapshot = {
    states: AircraftState[];
    trajectories: Trajectory[];
    conflicts: Conflict[];
};