import { useEffect, useState } from "react";

export const useTrajectories = () => {
    const URL = "/api/aircraft/trajectories";
    const [trajectories, setTrajectories] = useState<[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchTrajectories = async () => {
            setLoading(true);
            try {
                const response = await fetch(URL);

                // Check if the response status is successful
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const json = await response.json();
                setTrajectories(json);
            } catch (error) {
                console.error("Failed to fetch trajectories:", error);
                setError("Failed to fetch trajectories");
            } finally {
                setLoading(false);
            }
        };
        fetchTrajectories();
    }, []);

    return { trajectories, loading, error };
};