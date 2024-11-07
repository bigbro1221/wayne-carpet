// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import CustomSidebar from './components/SideBar';
import Users from './components/Users';
import ChatLogs from './components/ChatLogs';
import { ChatProvider } from './context/ChatContext'; // Updated to use ChatProvider
import './App.css';

function App() {
  return (
    <Router>
      <ChatProvider> {/* Use ChatProvider instead of DataProvider */}
        <div className="app-container" style={{ display: 'flex' }}>
          <CustomSidebar />
          <div className="main-content" style={{ padding: '20px', flex: 1 }}>
            <Routes>
              <Route path="/users" element={<Users />} />
              <Route path="/chat-logs/:id?" element={<ChatLogs />} />
            </Routes>
          </div>
        </div>
      </ChatProvider>
    </Router>
  );
}

export default App;
