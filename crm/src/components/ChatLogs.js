import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChat } from '../context/ChatContext';
import botIcon from '../assets/bot-icon.png';
import userIcon from '../assets/user-icon.png';
import { FaArrowDown } from 'react-icons/fa';

const formatContent = (content) => content.replace(/\\/g, ''); // Clean backslashes

const ChatLogs = () => {
  const { id: userId } = useParams();
  const navigate = useNavigate();
  const { users, messages, loadMessagesForUser, loadMoreMessages } = useChat();
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [scrollPositions, setScrollPositions] = useState({}); // Store scroll positions
  const [isInitialLoad, setIsInitialLoad] = useState(true); // Track initial load

  const [showScrollButton, setShowScrollButton] = useState(false);

  // Set the selected user and load messages
  useEffect(() => {
    const user = users.find((u) => String(u.user_id) === userId);
    if (user) {
      if (user !== selectedUser) {
        setSelectedUser(user);
        loadMessagesForUser(userId);
      }

      // Restore saved scroll position or scroll to bottom on the first load
      const container = messagesContainerRef.current;
      if (container) {
        if (scrollPositions[userId] !== undefined) {
          container.scrollTop = scrollPositions[userId];
        } else {
          scrollToBottom();
        }
      }
      setIsInitialLoad(false); // Mark initial load as complete
    } else {
      setSelectedUser(null);
    }
  }, [userId, users, loadMessagesForUser]); // Only run when userId changes

  // Save the scroll position for the current user
  const handleUserClick = (user) => {
    const container = messagesContainerRef.current;
    if (container) {
      setScrollPositions((prev) => ({
        ...prev,
        [userId]: container.scrollTop,
      }));
    }
    navigate(`/chat-logs/${user.user_id}`);
  };

  // Scroll to the bottom of the messages
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Handle scrolling and pagination
  const handleScroll = () => {
    const container = messagesContainerRef.current;
    if (container) {
      const shouldShowButton = container.scrollHeight > container.clientHeight &&
        container.scrollTop < container.scrollHeight - container.clientHeight - 50;
      setShowScrollButton(shouldShowButton);
    }
    if (container) {
      const isNearBottom =
        container.scrollHeight - container.scrollTop - container.clientHeight < 50;

      // Save current scroll position
      setScrollPositions((prev) => ({
        ...prev,
        [userId]: container.scrollTop,
      }));

      // Load more messages when scrolled past halfway
      if (container.scrollTop < container.scrollHeight / 2) {
        loadMoreMessages(userId);
      }
    }
  };

  // Attach and detach scroll event listener
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
    }
    return () => {
      if (container) {
        container.removeEventListener('scroll', handleScroll);
      }
    };
  }, [userId]); // Attach only when userId changes

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
        }}
      >
        <h2 style={{ marginBottom: '20px' }}>Users</h2>
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {users.map((user) => (
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
      <div
        className="chat-messages"
        style={{ flex: 1, padding: '20px', overflowY: 'auto', position: 'relative' }}
        ref={messagesContainerRef}
      >
        {selectedUser ? (
          <>
            <h2>Chat with {selectedUser.first_name} {selectedUser.last_name}</h2>
            <div className="messages">
              {messages[userId]?.length > 0 ? (
                messages[userId].map((message, index) => (
                  <div
                    key={index}
                    className={`chat-item ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
                  >
                    <img
                      src={message.role === 'user' ? userIcon : botIcon}
                      alt={message.role}
                      className="profile-icon"
                    />
                    <div
                      className={`chat-bubble ${message.role === 'user' ? 'user-bubble' : 'assistant-bubble'}`}
                      dangerouslySetInnerHTML={{ __html: formatContent(message.message) }}
                    />
                  </div>
                ))
              ) : (
                <p>No messages found for this user.</p>
              )}
              <div ref={messagesEndRef} />
            </div>
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
          </>
        ) : (
          <p>Select a user to view chat messages</p>
        )}
      </div>
    </div>
  );
};

export default ChatLogs;
