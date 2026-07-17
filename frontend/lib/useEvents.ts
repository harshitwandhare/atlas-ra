"use client";
import { useEffect, useRef, useState } from "react";
import { AgentEvent, WS } from "./api";

/** Live AgentEvent stream over WebSocket, with auto-reconnect. */
export function useEvents(max = 500): AgentEvent[] {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const retry = useRef(0);

  useEffect(() => {
    let ws: WebSocket;
    let closed = false;
    const connect = () => {
      ws = new WebSocket(WS);
      ws.onmessage = (m) => {
        const e = JSON.parse(m.data);
        if (e.type === "ping") return;
        setEvents((prev) => [e, ...prev].slice(0, max));
      };
      ws.onclose = () => {
        if (!closed) setTimeout(connect, Math.min(1000 * 2 ** retry.current++, 15000));
      };
      ws.onopen = () => (retry.current = 0);
    };
    connect();
    return () => {
      closed = true;
      ws.close();
    };
  }, [max]);

  return events;
}
