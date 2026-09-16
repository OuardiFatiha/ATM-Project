import { useEffect, useState } from "react";
import type { AircraftState } from "../types/AircraftState";

export const useAircraftStates = () => {
    const URL = "/api/aircraft/all";
    const [aircraftStates, setAircraftStates] = useState<AircraftState[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        let timeoutId: number | undefined;
        const controller = new AbortController();

        const fetchAircraftStates = async () => {
            setLoading(true);

            try {
                const response = await fetch(URL, { signal: controller.signal });

                if (!response.ok) {
                    if (response.status === 429) {
                        throw new Error("OpenSky rate limit exceeded. Try again later.");
                    }
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const json = await response.json();
                setAircraftStates(json);
                setError("");
            } catch (error) {
                if (error instanceof DOMException && error.name === "AbortError") {
                    return;
                }

                const message = error instanceof Error
                    ? error.message
                    : "Failed to fetch aircraft states";
                setError(message);
            } finally {
                setLoading(false);
                timeoutId = window.setTimeout(fetchAircraftStates, 10_000);
            }
        };

        fetchAircraftStates();

        return () => {
            controller.abort();
            if (timeoutId !== undefined) {
                window.clearTimeout(timeoutId);
            }
        };
    }, []);

    return { aircraftStates, loading, error };
};