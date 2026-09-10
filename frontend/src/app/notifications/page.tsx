"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import NotificationCard from "@/components/NotificationCard";
import { listNotifications, markAllNotificationsRead, markNotificationRead } from "@/services/matchingApi";
import type { Notification } from "@/types/Match";

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listNotifications()
      .then(setItems)
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  async function read(id: number) {
    const updated = await markNotificationRead(id);
    setItems((prev) => prev.map((n) => (n.id === id ? updated : n)));
  }

  async function readAll() {
    await markAllNotificationsRead();
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
  }

  const unread = items.filter((n) => !n.is_read).length;

  return (
    <AppShell title="Notifications">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-600">{unread} unread</p>
        <button className="btn-secondary" onClick={readAll} disabled={unread === 0}>
          Mark all read
        </button>
      </div>
      {loading ? (
        <p className="text-slate-600">Loading…</p>
      ) : items.length === 0 ? (
        <p className="text-slate-600">No notifications yet. You&apos;ll be alerted when new jobs match your CV.</p>
      ) : (
        <div className="space-y-3">
          {items.map((n) => (
            <NotificationCard key={n.id} notification={n} onRead={read} />
          ))}
        </div>
      )}
    </AppShell>
  );
}
