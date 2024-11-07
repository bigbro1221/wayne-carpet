// src/components/Users.js
import React, { useRef, useState } from 'react';
import { useChat } from '../context/ChatContext';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Toast } from 'primereact/toast';
import { InputText } from 'primereact/inputtext';
import { IconField } from 'primereact/iconfield';
import { InputIcon } from 'primereact/inputicon';

const Users = () => {
  const { users, loading } = useChat();
  const [globalFilterValue, setGlobalFilterValue] = useState('');
  const [filters, setFilters] = useState({
    global: { value: null, matchMode: 'contains' }
  });
  const toast = useRef(null);

  if (loading) {
    return <p>Loading users...</p>;
  }

  const footer = <p>Total users = {users ? users.length : 0}</p>;

  // Function to copy text to clipboard and show a toast notification
  const copyToClipboard = (username) => {
    navigator.clipboard.writeText(username).then(() => {
      toast.current.show({
        severity: 'success',
        summary: 'Copied',
        detail: `Username "${username}" copied to clipboard!`,
        life: 2000,
      });
    });
  };

  // Custom cell renderer for the Username column
  const usernameBodyTemplate = (rowData) => {
    let userName = '@' + rowData.username;
    return (
      <span
        onClick={() => copyToClipboard(userName)}
        style={{ cursor: 'pointer', color: '#00abc2', textDecoration: 'underline' }}
      >
        {userName}
      </span>
    );
  };

  const onGlobalFilterChange = (e) => {
    const value = e.target.value;
    const _filters = { ...filters };
    _filters['global'].value = value;

    setFilters(_filters); // Update filters state
    setGlobalFilterValue(value); // Update search input value
  };

  const renderHeader = () => {
    return (
      <div className="flex justify-content-end">
        <IconField iconPosition="left">
          <InputIcon className="pi pi-search" />
          <InputText value={globalFilterValue} onChange={onGlobalFilterChange} placeholder="Search" />
        </IconField>
      </div>
    );
  };

  const header = renderHeader();

  return (
    <div>
      <Toast ref={toast} /> {/* Toast component for feedback */}
      <DataTable
        value={users}
        responsiveLayout="scroll"
        size="small"
        showGridlines
        header={header}
        footer={footer}
        stripedRows
        removableSort
        rows={5}
        dataKey="id"
        tableStyle={{ minWidth: '50rem' }}
        paginator
        paginatorTemplate="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
        filters={filters} // Apply filters to DataTable
        globalFilterFields={['first_name', 'last_name', 'user_id', 'username']} // Fields to apply global filter
      >
        <Column field="first_name" header="First Name" sortable></Column>
        <Column field="last_name" header="Last Name"></Column>
        <Column field="user_id" header="User Id"></Column>

        {/* Custom column with click-to-copy functionality for Username */}
        <Column
          field="username"
          header="Username"
          body={usernameBodyTemplate} // Use the custom cell renderer
        ></Column>
      </DataTable>
    </div>
  );
};

export default Users;
