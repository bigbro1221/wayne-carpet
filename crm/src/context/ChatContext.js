// src/context/ChatContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { firestore } from '../firebase';
import { collection, onSnapshot, query, orderBy } from 'firebase/firestore';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [users, setUsers] = useState([]);
  const [messages, setMessages] = useState({});
  const [loading, setLoading] = useState(true);

  // Store unsubscribe functions for messages to clean up old listeners
  const messageUnsubscribers = {};

  // Fetch users when the app loads
  useEffect(() => {
    const usersRef = collection(firestore, 'users');
    const unsubscribeUsers = onSnapshot(usersRef, (snapshot) => {
      const usersData = snapshot.docs.map((doc) => ({
        user_id: doc.id,
        ...doc.data()
      }));
      setUsers(usersData);
      setLoading(false);
    });

    return () => unsubscribeUsers();
  }, []);

  // Function to load messages for a specific user and manage real-time updates
  const loadMessagesForUser = (userId) => {
    // If a listener already exists for this user, clear it first to avoid duplicates
    if (messageUnsubscribers[userId]) {
      messageUnsubscribers[userId](); // Unsubscribe from previous listener
    }

    const messagesRef = query(
      collection(firestore, `chat_logs/${userId}/messages`),
      orderBy('timestamp', 'asc') // Order messages by timestamp in ascending order
    );
    
    const unsubscribeMessages = onSnapshot(messagesRef, (snapshot) => {
      const userMessages = snapshot.docs.map((doc) => ({
        messageId: doc.id,
        ...doc.data()
      }));
    
      setMessages((prevMessages) => ({
        ...prevMessages,
        [userId]: userMessages
      }));
    });

    // Store the unsubscribe function for cleanup
    messageUnsubscribers[userId] = unsubscribeMessages;
  };

  // Clean up all message listeners when component unmounts
  useEffect(() => {
    return () => {
      Object.values(messageUnsubscribers).forEach(unsubscribe => unsubscribe());
    };
  }, []);

  return (
    <ChatContext.Provider value={{ users, messages, loadMessagesForUser, loading }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);
