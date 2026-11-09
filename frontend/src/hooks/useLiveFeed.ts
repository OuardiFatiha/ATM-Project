import { useEffect, useState } from "react";
import type { LiveSnapshot } from "../types/LiveSnapshot";

export const useLiveFeed = () => {
    const [liveSnapshot, setLiveSnapshot] = useState<LiveSnapshot | null>(null);
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        let socket: WebSocket | undefined;
        let retryTimeoutId: number | undefined;
        let retryDelay = 1_000;
        let cancelled = false;

        const connect = () => {
            const protocol = window.location.protocol === "https:" ? "wss" : "ws";
            socket = new WebSocket(`${protocol}://${window.location.host}/ws/live`);

            socket.onopen = () => {
                retryDelay = 1_000;
                setConnected(true);
                setError("");
            };

            socket.onmessage = (event) => {
                setLiveSnapshot(JSON.parse(event.data));
            };

            socket.onerror = () => {
                setError("Live feed connection error");
            };

            socket.onclose = () => {
                setConnected(false);
                if (cancelled) return;
                retryTimeoutId = window.setTimeout(connect, retryDelay);
                retryDelay = Math.min(retryDelay * 2, 30_000);
            };
        };

        connect();

        return () => {
            cancelled = true;
            window.clearTimeout(retryTimeoutId);
            socket?.close();
        };
    }, []);

    return { liveSnapshot, connected, error };
};
