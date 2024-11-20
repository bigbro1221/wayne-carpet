import React, { createContext, useContext, useState, useEffect } from 'react';
import { firestore } from '../firebase';
import { collection, query, orderBy, limit, startAfter, onSnapshot } from 'firebase/firestore';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [users, setUsers] = useState([]);
  const [messages, setMessages] = useState({});
  const lastVisibleMessages = {}; // Store the last fetched message for each user
  const isFullyLoaded = {}; // Track if all messages have been fetched for a user

  // Fetch all users
  useEffect(() => {
    const usersRef = collection(firestore, 'users');
    const unsubscribeUsers = onSnapshot(usersRef, (snapshot) => {
      const usersData = snapshot.docs.map((doc) => ({
        user_id: doc.id,
        ...doc.data(),
      }));
      setUsers(usersData);
    });

    return () => unsubscribeUsers();
  }, []);

  // Load initial messages for a user
  const loadMessagesForUser = (userId) => {
    if (isFullyLoaded[userId]) return; // Stop if all messages are loaded

    const messagesRef = query(
      collection(firestore, `chat_logs/${userId}/messages`),
      orderBy('timestamp', 'desc'),
      limit(30)
    );

    onSnapshot(messagesRef, (snapshot) => {
      const userMessages = snapshot.docs.map((doc) => ({
        messageId: doc.id,
        ...doc.data(),
      }));

      if (snapshot.docs.length > 0) {
        lastVisibleMessages[userId] = snapshot.docs[snapshot.docs.length - 1]; // Store the last visible message
      } else {
        isFullyLoaded[userId] = true; // Mark as fully loaded if no more messages
      }

      setMessages((prev) => ({
        ...prev,
        [userId]: [...(prev[userId] || []), ...userMessages.reverse()], // Reverse for ascending order
      }));
    });
  };

  // Load more messages for pagination
  const loadMoreMessages = (userId) => {
    if (isFullyLoaded[userId] || !lastVisibleMessages[userId]) return; // Stop if fully loaded or no last message

    const messagesRef = query(
      collection(firestore, `chat_logs/${userId}/messages`),
      orderBy('timestamp', 'desc'),
      startAfter(lastVisibleMessages[userId]), // Use the last fetched message
      limit(30)
    );

    onSnapshot(messagesRef, (snapshot) => {
      const userMessages = snapshot.docs.map((doc) => ({
        messageId: doc.id,
        ...doc.data(),
      }));

      if (snapshot.docs.length > 0) {
        lastVisibleMessages[userId] = snapshot.docs[snapshot.docs.length - 1]; // Update the last visible message
      } else {
        isFullyLoaded[userId] = true; // Mark as fully loaded if no more messages
      }

      setMessages((prev) => ({
        ...prev,
        [userId]: [...(prev[userId] || []), ...userMessages.reverse()], // Reverse for ascending order
      }));
    });
  };

  return (
    <ChatContext.Provider value={{ users, messages, loadMessagesForUser, loadMoreMessages }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);
