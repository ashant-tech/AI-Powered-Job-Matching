'use client';

interface NotificationCardProps {
  notification: {
    id: number;
    type: string;
    title: string;
    message: string;
    is_read: boolean;
    created_at: string;
  };
  onMarkAsRead?: (id: number) => void;
}

export default function NotificationCard({ notification, onMarkAsRead }: NotificationCardProps) {
  const getIcon = () => {
    switch (notification.type) {
      case 'match':
        return '🎯';
      case 'application':
        return '📝';
      case 'system':
        return '⚙️';
      default:
        return '🔔';
    }
  };

  return (
    <div
      className={`p-4 rounded-lg border ${
        notification.is_read ? 'bg-gray-50 border-gray-200' : 'bg-indigo-50 border-indigo-200'
      }`}
    >
      <div className="flex justify-between items-start">
        <div className="flex items-start gap-3 flex-1">
          <div className="text-2xl">{getIcon()}</div>
          <div className="flex-1">
            <h3 className={`font-semibold mb-1 ${notification.is_read ? 'text-gray-700' : 'text-gray-900'}`}>
              {notification.title}
            </h3>
            <p className="text-gray-600 text-sm mb-2">{notification.message}</p>
            <p className="text-gray-400 text-xs">
              {new Date(notification.created_at).toLocaleString()}
            </p>
          </div>
        </div>
        {!notification.is_read && onMarkAsRead && (
          <button
            onClick={() => onMarkAsRead(notification.id)}
            className="ml-4 text-indigo-600 hover:text-indigo-700 text-sm font-semibold"
          >
            Mark as read
          </button>
        )}
      </div>
    </div>
  );
}
