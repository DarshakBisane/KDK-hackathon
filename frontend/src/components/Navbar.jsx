import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Home,
  Briefcase,
  FileText,
  LayoutDashboard,
  Target,
  Compass,
  User as UserIcon,
  LogOut,
  Menu,
  X,
  ChevronDown
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const navLinks = isAuthenticated
    ? [
        { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
        { name: 'Career', path: '/career', icon: Briefcase },
        { name: 'Resume', path: '/resume', icon: FileText },
        { name: 'Skill Gap', path: '/skills', icon: Target },
        { name: 'Roadmap', path: '/roadmap', icon: Compass },
        { name: 'Profile', path: '/profile', icon: UserIcon },
      ]
    : [
        { name: 'Home', path: '/', icon: Home },
        { name: 'How It Works', path: '/#how-it-works', icon: Sparkles },
      ];

  const handleLogout = () => {
    logout();
    navigate('/login');
    setUserDropdownOpen(false);
    setMobileMenuOpen(false);
  };

  const getInitials = (name) => {
    if (!name) return 'S';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <header className="sticky top-0 z-40 px-4 sm:px-6 pt-3 pb-2 transition-all">
      <nav className="max-w-[1200px] mx-auto h-16 bg-white/95 backdrop-blur-md rounded-2xl border border-border-subtle shadow-nav flex items-center justify-between px-4 sm:px-6">
        
        {/* Left: Logo */}
        <Link
          to={isAuthenticated ? "/dashboard" : "/"}
          className="flex items-center gap-2.5 group cursor-pointer focus:outline-none"
        >
          <div className="w-9 h-9 rounded-xl bg-brand flex items-center justify-center text-white shadow-soft transition-transform group-hover:scale-105">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base tracking-tight text-text-primary group-hover:text-brand transition-colors">
              SkillGap<span className="text-brand">AI</span>
            </span>
            <span className="text-[10px] text-text-secondary -mt-1 font-medium hidden sm:inline">
              Student Career Platform
            </span>
          </div>
        </Link>

        {/* Center: Desktop Navigation Links */}
        <div className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path;
            const Icon = link.icon;
            return (
              <Link
                key={link.name}
                to={link.path}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-sm font-medium transition-all duration-200 transform hover:-translate-y-0.5 ${
                  isActive
                    ? 'bg-lavender text-brand font-semibold shadow-xs'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand' : 'text-text-muted'}`} />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>

        {/* Right: Auth Profile / Actions */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-2.5 p-1.5 pl-2.5 rounded-xl border border-border-subtle hover:border-border-hover bg-bg-secondary/60 hover:bg-bg-secondary transition-all cursor-pointer focus:outline-none"
              >
                <div className="w-7 h-7 rounded-lg bg-brand-light text-brand font-semibold text-xs flex items-center justify-center">
                  {getInitials(user?.name)}
                </div>
                <div className="text-left">
                  <p className="text-xs font-semibold text-text-primary leading-tight truncate max-w-[120px]">
                    {user?.name || 'Student'}
                  </p>
                  <p className="text-[10px] text-text-secondary truncate max-w-[120px]">
                    {user?.target_career_name || 'Set Goal'}
                  </p>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-text-muted mr-1" />
              </button>

              {/* User Dropdown Menu */}
              {userDropdownOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setUserDropdownOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl border border-border-subtle shadow-soft-lg py-1.5 z-20 animate-in fade-in slide-in-from-top-2 duration-150">
                    <div className="px-3.5 py-2 border-b border-border-subtle">
                      <p className="text-xs font-semibold text-text-primary truncate">{user?.name}</p>
                      <p className="text-[11px] text-text-secondary truncate">{user?.email}</p>
                    </div>
                    <Link
                      to="/profile"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-3.5 py-2 text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-bg-secondary transition-colors"
                    >
                      <UserIcon className="w-3.5 h-3.5 text-text-muted" />
                      View Profile
                    </Link>
                    <Link
                      to="/dashboard"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-3.5 py-2 text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-bg-secondary transition-colors"
                    >
                      <LayoutDashboard className="w-3.5 h-3.5 text-text-muted" />
                      Dashboard
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left flex items-center gap-2 px-3.5 py-2 text-xs font-medium text-status-danger hover:bg-red-50 transition-colors border-t border-border-subtle mt-1"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      Sign Out
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-4 py-1.5 text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-bg-secondary rounded-xl transition-all"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-1.5 text-sm font-medium text-white bg-brand hover:bg-brand-hover rounded-xl shadow-soft transition-all transform hover:-translate-y-0.5"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Hamburger Button */}
        <div className="flex md:hidden items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-text-secondary hover:text-text-primary hover:bg-bg-secondary focus:outline-none transition-colors"
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </nav>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden max-w-[1200px] mx-auto mt-2 bg-white rounded-2xl border border-border-subtle shadow-soft-lg p-4 animate-in fade-in slide-in-from-top-2 duration-200">
          {isAuthenticated && (
            <div className="flex items-center gap-3 p-3 mb-3 bg-bg-secondary rounded-xl border border-border-subtle">
              <div className="w-9 h-9 rounded-xl bg-brand-light text-brand font-semibold text-sm flex items-center justify-center">
                {getInitials(user?.name)}
              </div>
              <div className="flex-1 truncate">
                <p className="text-sm font-semibold text-text-primary truncate">{user?.name}</p>
                <p className="text-xs text-text-secondary truncate">{user?.email}</p>
              </div>
            </div>
          )}

          <div className="flex flex-col gap-1">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              const Icon = link.icon;
              return (
                <Link
                  key={link.name}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-lavender text-brand font-semibold'
                      : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand' : 'text-text-muted'}`} />
                  <span>{link.name}</span>
                </Link>
              );
            })}

            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-sm font-medium text-status-danger hover:bg-red-50 transition-colors mt-2 border-t border-border-subtle pt-3"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            ) : (
              <div className="flex flex-col gap-2 pt-3 border-t border-border-subtle mt-2">
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2.5 text-sm font-medium text-text-primary bg-bg-secondary rounded-xl"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2.5 text-sm font-medium text-white bg-brand rounded-xl shadow-soft"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
