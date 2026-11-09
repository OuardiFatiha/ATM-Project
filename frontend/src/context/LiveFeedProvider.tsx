import type { ReactNode } from "react";
import { useLiveFeed } from "../hooks/useLiveFeed";
import { LiveFeedContext } from "./LiveFeedContext";

export const LiveFeedProvider = ({ children }: { children: ReactNode }) => {
    const { liveSnapshot, connected, error } = useLiveFeed();

    return (
        <LiveFeedContext.Provider value={{ liveSnapshot, connected, error }}>
            {children}
        </LiveFeedContext.Provider>
    );
};