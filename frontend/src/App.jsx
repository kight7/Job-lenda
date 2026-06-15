import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './services/firebase';
import { Briefcase, LayoutDashboard, FileText, Send, Users, LogOut, Loader2 } from 'lucide-react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import JobSearch from './pages/JobSearch';
import Applications from './pages/Applications';

// Placeholder Pages (To be built later)
const Tailor = () => <div className="p-8"><h1 className="text-3xl font-bold text-gray-900 mb-4">Resume Tailor</h1><p className="text-gray-600">Tailor your resume for specific opportunities.</p></div>;
const Outreach = () => <div className="p-8"><h1 className="text-3xl font-bold text-gray-900 mb-4">Outreach</h1><p className="text-gray-600">Draft networking messages and emails.</p></div>;
const Interview = () => <div className="p-8"><h1 className="text-3xl font-bold text-gray-900 mb-4">Interview Prep</h1><p className="text-gray-600">Practice behavioral and technical questions.</p></div>;

const Navbar = () => {
  const location = useLocation();
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/search', label: 'Search', icon: Briefcase },
    { path: '/tailor', label: 'Tailor', icon: FileText },
    { path: '/applications', label: 'Applications', icon: FileText },
    { path: '/outreach', label: 'Outreach', icon: Send },
    { path: '/interview', label: 'Interview', icon: Users },
  ];

  const handleLogout = async () => {
    await signOut(auth);
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Briefcase className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900 tracking-tight">AI Job Agent</span>
            </div>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`${
                      isActive
                        ? 'border-blue-600 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200`}
                  >
                    <Icon className={`w-4 h-4 mr-2 ${isActive ? 'text-blue-600' : 'text-gray-400'}`} />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
          <div className="flex items-center">
            <button
              onClick={handleLogout}
              className="inline-flex items-center px-3 py-2 border border-gray-200 text-sm leading-4 font-medium rounded-md text-gray-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <LogOut className="w-4 h-4 mr-2 text-gray-400" />
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

const ProtectedRoute = ({ children, user }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Navbar />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  );
};

const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Listen for Firebase Auth state changes
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <Loader2 className="w-10 h-10 animate-spin text-blue-600 mb-4" />
        <p className="text-gray-500 font-medium">Starting AI Job Agent...</p>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Route */}
        <Route 
          path="/login" 
          element={user ? <Navigate to="/" replace /> : <Login />} 
        />
        
        {/* Protected Routes */}
        <Route path="/" element={<ProtectedRoute user={user}><Dashboard /></ProtectedRoute>} />
        <Route path="/search" element={<ProtectedRoute user={user}><JobSearch /></ProtectedRoute>} />
        <Route path="/tailor" element={<ProtectedRoute user={user}><Tailor /></ProtectedRoute>} />
        <Route path="/applications" element={<ProtectedRoute user={user}><Applications /></ProtectedRoute>} />
        <Route path="/outreach" element={<ProtectedRoute user={user}><Outreach /></ProtectedRoute>} />
        <Route path="/interview" element={<ProtectedRoute user={user}><Interview /></ProtectedRoute>} />
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
