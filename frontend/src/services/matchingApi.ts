import type { Match, Notification } from "@/types/Match";
import { request } from "./apiClient";

export function runMatching(limit = 20) {
  return request<Match[]>(`/api/matching/run?limit=${limit}`, { method: "POST" });
}

export function getRecommendations(limit = 20) {
  return request<Match[]>(`/api/matching/recommendations?limit=${limit}`);
}

export function listNotifications(unreadOnly = false) {
  return request<Notification[]>(`/api/notifications?unread_only=${unreadOnly}`);
}

export function markNotificationRead(id: number) {
  return request<Notification>(`/api/notifications/${id}/read`, { method: "POST" });
}

export function markAllNotificationsRead() {
  return request<{ updated: number }>("/api/notifications/read-all", { method: "POST" });
}
