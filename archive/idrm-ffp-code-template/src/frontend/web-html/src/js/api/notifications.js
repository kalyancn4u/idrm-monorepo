/**
 * js/api/notifications.js — notification API calls (built on the core `apiFetch`).
 *   listNotifications     → GET  /notifications        → { status, data: { items, unread_count } }
 *   markNotificationRead  → POST /notifications/{id}/read → the updated NotificationOut
 *
 * (Canonical paths — there is no PUT or a "read-all" endpoint in the MVP API.)
 */
import { apiFetch } from "./client.js";

/** The signed-in user's notifications, newest first, plus an unread count. */
export const listNotifications = () => apiFetch("/notifications");

/** Mark one notification read. */
export const markNotificationRead = (id) => apiFetch(`/notifications/${id}/read`, { method: "POST" });
