// src/components/ChatLogs.js
import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChat } from '../context/ChatContext';
import botIcon from '../assets/bot-icon.png';
import userIcon from '../assets/user-icon.png';
import { FaArrowDown } from 'react-icons/fa';

const formatContent = (content) => content.replace(/\\/g, ''); // Clean backslashes

const ChatLogs = () => {
  const { id } = useParams(); // Get the user_id from the route
  const navigate = useNavigate();
  const { users, messages, loadMessagesForUser } = useChat();
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showScrollButton, setShowScrollButton] = useState(false);

  useEffect(() => {
    // Find the user based on the route 'id'
    const user = users.find((u) => u.user_id == id);
    if (user) {
      setSelectedUser(user); // Set selected user
      loadMessagesForUser(user.user_id); // Load messages for this user
    } else {
      setSelectedUser(null); // Clear selection if no valid user
    }
  }, [id, users, loadMessagesForUser]); // Depend on 'id' to re-trigger on route change

  const handleUserClick = (user) => {
    // Update URL to reflect the selected user, staying on the same page
    navigate(`/chat-logs/${user.user_id}`);
  };

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleScroll = () => {
    const container = messagesContainerRef.current;
    if (container) {
      const shouldShowButton = container.scrollHeight > container.clientHeight &&
        container.scrollTop < container.scrollHeight - container.clientHeight - 50;
      setShowScrollButton(shouldShowButton);
    }
  };

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener("scroll", handleScroll);
      handleScroll();
    }
    return () => {
      if (container) {
        container.removeEventListener("scroll", handleScroll);
      }
    };
  }, [messages[selectedUser?.user_id]]);

  return (
    <div className="chat-logs-container" style={{ display: 'flex', flexGrow: 1 }}>
      {/* User Sidebar */}
      <div
        className="user-sidebar"
        style={{
          width: '250px',
          padding: '20px',
          backgroundColor: '#1a1a2e',
          color: '#ffffff',
          overflowY: 'auto',
          boxShadow: '2px 0 5px rgba(0,0,0,0.1)',
        }}
      >
        <h2 style={{ color: '#ffffff', fontSize: '1.2em', marginBottom: '20px' }}>Users</h2>
        <ul style={{ listStyleType: 'none', padding: '0' }}>
          {users.map(user => (
            <li
              key={user.user_id}
              onClick={() => handleUserClick(user)}
              style={{
                cursor: 'pointer',
                padding: '10px',
                backgroundColor: selectedUser?.user_id === user.user_id ? '#3d3d5c' : 'transparent',
                fontWeight: selectedUser?.user_id === user.user_id ? 'bold' : 'normal',
                color: selectedUser?.user_id === user.user_id ? '#ffffff' : '#cccccc',
                borderRadius: '5px',
                marginBottom: '5px',
              }}
            >
              {user.first_name} {user.last_name} ({user.username})
            </li>
          ))}
        </ul>
      </div>

      {/* Chat Messages Area */}
      <div className="chat-messages" style={{ flex: 1, padding: '20px', overflowY: 'auto', position: 'relative'}}>
        {selectedUser ? (
          <div>
            <h2>Chat with {selectedUser.first_name} {selectedUser.last_name}</h2>
            <div
              className="messages"
              ref={messagesContainerRef}
              style={{ position: 'relative', overflowY: 'auto', maxHeight: '80vh' }}
            >
              {messages[selectedUser.user_id]?.length > 0 ? (
                messages[selectedUser.user_id].map((message, index) => (
                  <div key={index} className={`chat-item ${message.role === "user" ? "user-message" : "assistant-message"}`}>
                    <img
                      src={message.role === "user" ? userIcon : botIcon}
                      alt={message.role}
                      className="profile-icon"
                    />
                    <div
                      className={`chat-bubble ${message.role === "user" ? "user-bubble" : "assistant-bubble"}`}
                      dangerouslySetInnerHTML={{ __html: formatContent(message.message) }}
                    />
                  </div>
                ))
              ) : (
                <p>No messages found for this user.</p>
              )}
              <div ref={messagesEndRef} />
            </div>
            {/* Floating Scroll-to-Bottom Button */}
            <FaArrowDown
              onClick={scrollToBottom}
              style={{
                position: 'absolute',
                bottom: '20px',
                left: '50%',
                transform: `translateX(-50%) scale(${showScrollButton ? 1 : 0.5})`,
                backgroundColor: 'rgba(0, 123, 255, 0.8)',
                color: 'white',
                borderRadius: '50%',
                padding: '10px',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.1)',
                opacity: showScrollButton ? 0.8 : 0,
                pointerEvents: showScrollButton ? 'auto' : 'none',
                transition: 'opacity 0.3s ease, transform 0.3s ease',
              }}
            />
          </div>
        ) : (
          <p>Select a user to view chat messages</p>
        )}
      </div>
    </div>
  );
};

export default ChatLogs;
