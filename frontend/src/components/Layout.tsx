import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Moon } from 'lucide-react';

const Layout = ({ children }: { children: React.ReactNode }) => {
  const { userEmail, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Animated background */}
      <div className="bg-mesh" />
      <div className="bg-mesh-extra" />
      <div className="bg-grid" />

      <div className="app-container">
        {/* Navbar */}
        <nav className="navbar">
          <div className="navbar-brand">
            <div className="navbar-brand-icon">
              <Moon size={22} color="white" />
            </div>
            <span className="navbar-brand-text">SleepAI</span>
          </div>

          <div className="navbar-user">
            <div className="navbar-email">
              <User size={16} />
              <span>{userEmail}</span>
            </div>
            <button className="btn btn-danger" onClick={handleLogout}>
              <LogOut size={14} />
              Çıkış
            </button>
          </div>
        </nav>

        {/* Page content */}
        <main>{children}</main>
      </div>
    </>
  );
};

export default Layout;
