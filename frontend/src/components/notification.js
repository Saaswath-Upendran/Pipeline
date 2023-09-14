import React from 'react';
import { Message } from 'semantic-ui-react';

const Notification = ({ notifications, removeNotification }) => {
  return (
    <div className="notification-container">
      {notifications.map((notification, index) => (
        <Message
          key={index}
          className={`notification ${notification.type}`}
          onDismiss={() => removeNotification(notification)}
        >
          {notification.message}
        </Message>
      ))}
    </div>
  );
};



export default Notification;

