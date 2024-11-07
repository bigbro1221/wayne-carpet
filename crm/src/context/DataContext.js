// src/context/DataContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { firestore } from '../firebase';
import { collection, onSnapshot } from 'firebase/firestore';

const DataContext = createContext();

export const useData = () => {
  return useContext(DataContext);
};

export const DataProvider = ({ children }) => {
  const [users, setUsers] = useState([]);
  const [chatLogs, setChatLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set up a real-time listener for users
    const usersCollection = collection(firestore, 'users');
    const usersUnsubscribe = onSnapshot(usersCollection, (snapshot) => {
      const usersData = snapshot.docs.map(doc => ({ user_id: doc.id, ...doc.data() }));
      setUsers(usersData);
      console.log("Users data loaded:", usersData);
    });

    // Set up a listener for the chat_logs collection
    const chatLogsCollection = collection(firestore, 'chat_logs');
    const chatLogsUnsubscribe = onSnapshot(chatLogsCollection, (snapshot) => {
      console.log("Snapshot for chat_logs received:", snapshot.size, "documents");

      snapshot.docs.forEach((chatDoc) => {
        const userId = chatDoc.id;
        const userData = chatDoc.data().user;

        // Listen for changes in the messages subcollection for each user document
        const messagesRef = collection(firestore, `chat_logs/${userId}/messages`);
        const messagesUnsubscribe = onSnapshot(messagesRef, (messagesSnapshot) => {
          const messages = messagesSnapshot.docs.map(msgDoc => ({
            messageId: msgDoc.id,
            ...msgDoc.data(),
          }));

          // Update the chatLogs state by user ID
          setChatLogs(prevChatLogs => {
            const updatedChatLogs = prevChatLogs.filter(log => log.user.user_id !== userId);
            return [...updatedChatLogs, { user: { user_id: userId, ...userData }, chat_logs: messages }];
          });

          console.log(`Messages for user ID ${userId} loaded:`, messages);
        });

        // Clean up the messages listener for each user when they are unmounted
        return () => messagesUnsubscribe();
      });

      setLoading(false);
    });

    // Clean up listeners on component unmount
    return () => {
      usersUnsubscribe();
      chatLogsUnsubscribe();
    };
  }, []);

  return (
    <DataContext.Provider value={{ users, chatLogs, loading }}>
      {children}
    </DataContext.Provider>
  );
};
