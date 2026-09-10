import type { Notification } from "@/types/Match";

type Props = { notification: Notification; onRead?: (id: number) => void };

export default function NotificationCard({ notification, onRead }: Props) {
  return (
    <div className={`card flex items-start gap-3 ${notification.is_read ? "opacity-70" : "border-indigo-200 bg-indigo-50/40"}`}>
      <span className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${notification.is_read ? "bg-slate-300" : "bg-indigo-600"}`} />
      <div className="flex-1">
        <p className="font-medium text-slate-900">{notification.title}</p>
        <p className="text-sm text-slate-700">{notification.message}</p>
        <p className="mt-1 text-xs text-slate-500">
          {new Date(notification.created_at).toLocaleString()} · {notification.channel}
        </p>
      </div>
      {!notification.is_read && onRead && (
        <button onClick={() => onRead(notification.id)} className="text-xs font-medium text-indigo-600 hover:underline">
          Mark read
        </button>
      )}
    </div>
  );
}
