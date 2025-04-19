import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { useNotification } from './NotificationContext';
import { Notification } from './Notification';

export function NotificationContainer() {
  const { notifications, removeNotification } = useNotification();

  return (
    <div className="fixed inset-0 flex items-end px-4 py-6 pointer-events-none sm:p-6 sm:items-start z-50">
      <div className="w-full flex flex-col items-center space-y-4 sm:items-end">
        <AnimatePresence>
          {notifications.map((notification) => (
            <Notification
              key={notification.id}
              {...notification}
              onClose={removeNotification}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
} 