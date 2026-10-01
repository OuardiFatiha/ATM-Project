import { useEffect, useState } from "react";
import type { Conflict } from "../types/Conflict";

export const useConflicts = () => {
    const URL = "/api/aircraft/conflicts";
    const [conflicts, setConflicts] = useState<Conflict[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        let timeoutId: number | undefined;
        const controller = new AbortController();

        const fetchConflicts = async () => {
            setLoading(true);
            try {
                const response = await fetch(URL, { signal: controller.signal });

                // Check if the response status is successful
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const json = await response.json();
                setConflicts(json);
                setError("");
            } catch (error) {
                if (error instanceof DOMException && error.name === "AbortError") {
                    return;
                }

                console.error("Failed to fetch conflicts:", error);
                setError("Failed to fetch conflicts");
            } finally {
                setLoading(false);
                timeoutId = window.setTimeout(fetchConflicts, 10_000);
            }
        };
        fetchConflicts();

        return () => {
            controller.abort();
            if (timeoutId !== undefined) {
                window.clearTimeout(timeoutId);
            }
        };
    }, []);

    return { conflicts, loading, error };
};
