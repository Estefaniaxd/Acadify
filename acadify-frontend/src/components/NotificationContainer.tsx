import React from 'react';
import { useNotification, Notification } from '../contexts/NotificationContext';

const NotificationItem: React.FC<{ notification: Notification }> = ({ notification }) => {
  const { removeNotification } = useNotification();

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return 'ℹ️';
    }
  };

  const getBackgroundColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-100 border-green-500 text-green-700';
      case 'error':
        return 'bg-red-100 border-red-500 text-red-700';
      case 'warning':
        return 'bg-yellow-100 border-yellow-500 text-yellow-700';
      case 'info':
        return 'bg-blue-100 border-blue-500 text-blue-700';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-700';
    }
  };

  return (
    <div className={`border-l-4 p-4 mb-3 rounded-r-lg shadow-lg ${getBackgroundColor()} animate-slide-in`}>
      <div className="flex items-start">
        <span className="text-xl mr-3">{getIcon()}</span>
        <div className="flex-1">
          <h4 className="font-semibold text-sm">{notification.title}</h4>
          <p className="text-sm mt-1">{notification.message}</p>
        </div>
        <button
          onClick={() => removeNotification(notification.id)}
          className="ml-4 text-gray-500 hover:text-gray-700 focus:outline-none"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

const NotificationContainer: React.FC = () => {
  const { notifications } = useNotification();

  if (notifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map(notification => (
        <NotificationItem key={notification.id} notification={notification} />
      ))}
    </div>
  );
};

export default NotificationContainer;
