"use client";
import { useEffect, useRef, useState } from "react";
import { AgentEvent, WS, markDemo } from "./api";

/**
 * Live AgentEvent stream over WebSocket, with auto-reconnect.
 *
 * If the socket never opens — no backend running, or the public deployment —
 * the hook serves the sample stream instead so the screen is not just blank.
 * Reconnection keeps running in the background, so starting `atlas serve`
 * swaps in real events without a reload.
 */
export function useEvents(max = 500): AgentEvent[] {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const retry = useRef(0);
  const everOpened = useRef(false);

  useEffect(() => {
    let ws: WebSocket;
    let closed = false;
    let timer: ReturnType<typeof setTimeout>;

    const loadDemo = async () => {
      markDemo(true);
      const { DEMO_EVENTS } = await import("./demo");
      setEvents((prev) => (prev.length ? prev : DEMO_EVENTS));
    };

    const connect = () => {
      ws = new WebSocket(WS);
      ws.onmessage = (m) => {
        const e = JSON.parse(m.data);
        if (e.type === "ping") return;
        setEvents((prev) => [e, ...prev].slice(0, max));
      };
      ws.onclose = () => {
        // A socket that never opened means there is nothing to talk to.
        if (!everOpened.current) void loadDemo();
        if (!closed) timer = setTimeout(connect, Math.min(1000 * 2 ** retry.current++, 15000));
      };
      ws.onopen = () => {
        everOpened.current = true;
        retry.current = 0;
        markDemo(false);
        setEvents([]); // drop the samples once real events can arrive
      };
    };

    connect();
    return () => {
      closed = true;
      clearTimeout(timer);
      ws.close();
    };
  }, [max]);

  return events;
}
