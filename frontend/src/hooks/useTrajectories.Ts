import { useEffect, useState } from "react";
import type { Trajectory } from "../types/Trajectory";

export const useTrajectories = () => {
    const URL = "/api/aircraft/trajectories";
    const [trajectories, setTrajectories] = useState<Trajectory[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        let timeoutId: number | undefined;
        const controller = new AbortController();

        const fetchTrajectories = async () => {
            setLoading(true);
            try {
                const response = await fetch(URL, { signal: controller.signal });

                // Check if the response status is successful
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const json = await response.json();
                setTrajectories(json);
                setError("");
            } catch (error) {
                if (error instanceof DOMException && error.name === "AbortError") {
                    return;
                }

                console.error("Failed to fetch trajectories:", error);
                setError("Failed to fetch trajectories");
            } finally {
                setLoading(false);
                timeoutId = window.setTimeout(fetchTrajectories, 10_000);
            }
        };
        fetchTrajectories();

        return () => {
            controller.abort();
            if (timeoutId !== undefined) {
                window.clearTimeout(timeoutId);
            }
        };
    }, []);

    return { trajectories, loading, error };
};