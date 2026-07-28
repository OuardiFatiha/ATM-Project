import { useEffect, useState } from "react";
import type { AircraftState } from "../types/AircraftState";

export const useAircraftStates = () => {
    const URL = "/api/aircraft/all?min_latitude=48.8&max_latitude=49.0&min_longitude=2.2&max_longitude=2.5";
    const [aircraftStates, setAircraftStates] = useState<AircraftState[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchAircraftStates = async () => {
            setLoading(true);
            try {
                const response = await fetch(URL);

                // Check if the response status is successful
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const json = await response.json();
                setAircraftStates(json);
            } catch (error) {
                console.error("Failed to fetch aircraft states:", error);
                setError("Failed to fetch aircraft states");
            } finally {
                setLoading(false);
            }
        };
        fetchAircraftStates();
    }, []);

    return { aircraftStates, loading, error };
};