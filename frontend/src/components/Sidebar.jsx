import React from 'react';
import { LayoutGrid, Calendar, Users, Heart, MessageSquare, Plus, Settings } from 'lucide-react';
import { useSession } from '../context/SessionContext';

const Sidebar = () => {
  const { clearSession } = useSession();

  const navItems = [
    { icon: LayoutGrid, label: 'Dashboard', active: false },
    { icon: Calendar, label: 'Appointments', active: false },
    { icon: Users, label: 'Doctors', active: false },
    { icon: MessageSquare, label: 'Chat', active: true },
    { icon: Heart, label: 'Health', active: false },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">A</div>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button 
            key={item.label} 
            className={`nav-item ${item.active ? 'active' : ''}`}
            title={item.label}
          >
            <item.icon size={22} />
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="nav-item" title="Settings">
          <Settings size={22} />
        </button>
        <button className="new-chat-fab" onClick={() => {
          clearSession();
          window.location.href = '/';
        }}>
          <Plus size={24} />
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
