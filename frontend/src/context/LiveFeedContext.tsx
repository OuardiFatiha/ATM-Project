import { createContext, useContext } from "react";
import type { LiveSnapshot } from "../types/LiveSnapshot";

export const LiveFeedContext = createContext<{
    liveSnapshot: LiveSnapshot | null;
    connected: boolean;
    error: string;
}>({
    liveSnapshot: null,
    connected: false,
    error: "",
});

export const useLiveFeedContext = () => useContext(LiveFeedContext);