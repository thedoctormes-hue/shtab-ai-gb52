import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Brain,
  Home,
  Search,
  Users,
  Settings,
  LogOut,
} from 'lucide-react';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const { logout } = useAuth();

  const navItems = [
    { path: '/home', label: 'Главная', icon: Home },
    { path: '/search', label: 'Поиск', icon: Search },
    { path: '/people', label: 'Люди', icon: Users },
    { path: '/settings', label: 'Настройки', icon: Settings },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Desktop Sidebar */}
      <aside
        className="hidden lg:flex flex-col w-[240px] h-full flex-shrink-0"
        style={{
          backgroundColor: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border-color)',
        }}
      >
        {/* Logo */}
        <div className="px-4 pt-6 pb-4">
          <Link to="/home" className="flex items-center gap-3 px-3">
            <Brain size={24} style={{ color: 'var(--accent)' }} />
            <span className="font-display text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
              LabDoctorM
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-2 space-y-1">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150"
              style={{
                backgroundColor: isActive(item.path) ? 'var(--accent-soft)' : 'transparent',
                color: isActive(item.path) ? 'var(--accent)' : 'var(--text-secondary)',
              }}
              onMouseEnter={e => {
                if (!isActive(item.path)) {
                  e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
                }
              }}
              onMouseLeave={e => {
                if (!isActive(item.path)) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Logout */}
        <div className="px-3 pb-6 pt-2" style={{ borderTop: '1px solid var(--border-color)' }}>
          <button
            onClick={logout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium w-full transition-all duration-150"
            style={{ color: 'var(--text-secondary)' }}
            onMouseEnter={e => {
              e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <LogOut size={18} />
            <span>Выход</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Mobile Top Bar */}
        <div
          className="lg:hidden flex items-center justify-between px-4 py-3 flex-shrink-0"
          style={{
            borderBottom: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-secondary)',
          }}
        >
          <Link to="/home" className="flex items-center gap-2">
            <Brain size={22} style={{ color: 'var(--accent)' }} />
            <span className="font-display text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
              LabDoctorM
            </span>
          </Link>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-[720px] mx-auto px-4 md:px-6 lg:px-8 py-6 lg:py-8">
            {children}
          </div>
        </div>

        {/* Mobile Bottom Navigation */}
        <div
          className="lg:hidden flex items-center justify-around py-2 flex-shrink-0"
          style={{
            borderTop: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-secondary)',
          }}
        >
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className="flex flex-col items-center gap-0.5 py-1 px-3 rounded-lg transition-all duration-150"
              style={{
                color: isActive(item.path) ? 'var(--accent)' : 'var(--text-tertiary)',
              }}
            >
              <item.icon size={20} />
              <span className="text-[10px] font-medium">{item.label}</span>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Layout;
