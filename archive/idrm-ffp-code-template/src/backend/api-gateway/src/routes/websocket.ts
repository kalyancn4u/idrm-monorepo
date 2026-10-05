/**
 * routes/websocket.ts — real-time fan-out (Module G4).
 *
 * Browsers open a WebSocket to the gateway (ws://localhost:3001) and send
 *     { "type": "subscribe", "channel": "service_requests" }
 * to start receiving live events. The backend (M5) PUBLISHES those events to Redis
 * channels (`service_requests`, `notifications`); this module SUBSCRIBES to Redis
 * and relays each message to every client subscribed to that channel:
 *
 *     Backend ──publish──▶ Redis channel ──(this bridge)──▶ subscribed WS clients
 *
 * 🚩 Without `REDIS_URL` set, the socket still works (clients connect + subscribe),
 * but no backend events arrive — there is nothing publishing for us to relay.
 */
import { RedisClient, type ServerWebSocket } from "bun";

import { config } from "../config";

/** Per-connection state: the set of channels this socket is subscribed to. */
export interface WsData {
  channels: Set<string>;
}

type Client = ServerWebSocket<WsData>;

// channel name → the set of sockets currently subscribed to it.
const subscribers = new Map<string, Set<Client>>();

// Redis channels we relay — must match the backend's names in core/redis.py.
const RELAYED_CHANNELS = ["service_requests", "notifications"];

function addSubscriber(channel: string, ws: Client): void {
  let set = subscribers.get(channel);
  if (!set) {
    set = new Set();
    subscribers.set(channel, set);
  }
  set.add(ws);
  ws.data.channels.add(channel);
}

function removeSubscriber(channel: string, ws: Client): void {
  subscribers.get(channel)?.delete(ws);
  ws.data.channels.delete(channel);
}

/**
 * Send a raw message to every socket subscribed to `channel`.
 * @returns how many clients it was delivered to (dead sockets are pruned).
 */
export function broadcast(channel: string, message: string): number {
  const set = subscribers.get(channel);
  if (!set || set.size === 0) return 0;
  let delivered = 0;
  for (const ws of set) {
    try {
      ws.send(message);
      delivered++;
    } catch {
      set.delete(ws); // socket already closed — drop it
    }
  }
  return delivered;
}

// ---- Bun.serve websocket handlers ------------------------------------------
/** New connection: greet the client. (Its `channels` set is created at upgrade.) */
export function handleOpen(ws: Client): void {
  if (!ws.data.channels) ws.data.channels = new Set();
  ws.send(JSON.stringify({ type: "connected" }));
}

/** A client message: `{type:"subscribe"|"unsubscribe"|"ping", channel?}`. */
export function handleMessage(ws: Client, raw: string | Buffer): void {
  let msg: { type?: string; channel?: string };
  try {
    msg = JSON.parse(typeof raw === "string" ? raw : raw.toString());
  } catch {
    ws.send(JSON.stringify({ type: "error", detail: "Invalid JSON" }));
    return;
  }

  const channel = msg.channel ?? "service_requests";
  switch (msg.type) {
    case "subscribe":
      addSubscriber(channel, ws);
      ws.send(JSON.stringify({ type: "subscribed", channel }));
      break;
    case "unsubscribe":
      removeSubscriber(channel, ws);
      ws.send(JSON.stringify({ type: "unsubscribed", channel }));
      break;
    case "ping":
      ws.send(JSON.stringify({ type: "pong" }));
      break;
    default:
      ws.send(JSON.stringify({ type: "error", detail: `Unknown message type: ${msg.type}` }));
  }
}

/** Connection closed: remove the socket from every channel it was in. */
export function handleClose(ws: Client): void {
  for (const channel of ws.data.channels ?? []) subscribers.get(channel)?.delete(ws);
  ws.data.channels?.clear();
}

// ---- Redis → WebSocket bridge ----------------------------------------------
/**
 * Subscribe to the backend's Redis channels and relay each published message to
 * the WebSocket clients subscribed to that channel.
 *
 * Best-effort: if `REDIS_URL` isn't set we skip (clients still connect, just
 * receive nothing); if the subscribe fails we log and carry on. A subscriber needs
 * its own connection, so this `RedisClient` is dedicated to pub/sub.
 */
export async function startRedisBridge(): Promise<void> {
  if (!config.redisUrl) {
    console.log("WebSocket: REDIS_URL not set — clients can connect, but no backend events will be relayed.");
    return;
  }
  try {
    const subscriber = new RedisClient(config.redisUrl);
    for (const channel of RELAYED_CHANNELS) {
      // Bun calls the listener with (message, channel); we relay the raw message.
      await subscriber.subscribe(channel, (message: string) => broadcast(channel, message));
    }
    console.log(`WebSocket: subscribed to Redis channels [${RELAYED_CHANNELS.join(", ")}]`);
  } catch (err) {
    console.warn("WebSocket: Redis subscribe failed — real-time relay disabled:", err);
  }
}
