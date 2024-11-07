// src/components/Sidebar.js
import React, { useState } from 'react';
import { Sidebar, Menu, MenuItem, SubMenu, sidebarClasses } from 'react-pro-sidebar';
import { Link } from 'react-router-dom';
import { FaUsers, FaComments, FaChartPie, FaCalendar } from 'react-icons/fa';
import logo from '../assets/logo.png'; // Replace with the path to your logo image

const CustomSidebar = () => {
  const [collapsed, setCollapsed] = useState(true); // Sidebar is collapsed by default

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  return (
    <Sidebar
      collapsed={collapsed}
      rootStyles={{
        [`.${sidebarClasses.container}`]: {
          backgroundColor: '#ffffff', // White background color
          color: '#000000',
        },
      }}
      width="250px"
      collapsedWidth="80px" // Width when collapsed
      defaultCollapsed
    >
      <div 
        onClick={toggleSidebar} 
        style={{
          padding: '10px', 
          cursor: 'pointer', 
          display: 'flex', 
          justifyContent: 'center',
          alignItems: 'center',
          borderBottom: '1px solid #ddd'
        }}
      >
        <img src={logo} alt="Logo" style={{ width: collapsed ? '20px' : '20px', transition: 'width 0.3s' }} />
      </div>

      <Menu
        menuItemStyles={{
          button: {
            color: '#000000', // Default text color
            [`&.active`]: {
              backgroundColor: '#e0e0e0', // Background for active items
              color: '#1f4068',
            },
            '&:hover': {
              backgroundColor: '#abd9f7', // Light blue hover effect
            },
          },
          icon: {
            color: '#000000',
          },
          label: {
            fontSize: '16px',
            color: '#000000',
          },
        }}
      >
        <MenuItem icon={<FaUsers />} component={<Link to="/users" />}>Users</MenuItem>
        <MenuItem icon={<FaComments />} component={<Link to="/chat-logs" />}>Chat Logs</MenuItem>
        <SubMenu label="More Options" icon={<FaChartPie />}>
          <MenuItem component={<Link to="/reports" />}>Reports</MenuItem>
          <MenuItem component={<Link to="/analytics" />}>Analytics</MenuItem>
        </SubMenu>
        <MenuItem icon={<FaCalendar />} component={<Link to="/calendar" />}>Calendar</MenuItem>
      </Menu>
    </Sidebar>
  );
};

export default CustomSidebar;
