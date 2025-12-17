import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import PaymentForm from './components/PaymentForm';
import TransactionTracker from './components/TransactionTracker';
import Login from './components/Login';
import LiveDemo from './components/LiveDemo';
import { fetchRecentPayments, getCurrentUser, logout } from './utils/api';

function AppContent() {
  const [activeTab, setActiveTab] = useState('create'); // 'create' or 'track'
  const [recentPayments, setRecentPayments] = useState([]);
  const [stats, setStats] = useState({ total: 0, volume: 0, success: 0 });
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [demoMode, setDemoMode] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Load recent payments when authenticated or demo mode changes
  useEffect(() => {
    if (user || demoMode) { // Load payments if user is logged in OR demo mode is active
      loadRecentPayments();
    } else {
      setRecentPayments([]); // Clear payments if neither logged in nor demo mode
      setStats({ total: 0, volume: 0, success: 0 });
    }
  }, [user, demoMode]); // Dependency on user and demoMode

  const checkAuth = async () => {
    try {
      const currentUser = await getCurrentUser();
      if (currentUser && currentUser.user_id) {
        setUser(currentUser);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.log('Auth check failed:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      setRecentPayments([]);
      setStats({ total: 0, volume: 0, success: 0 });
      setDemoMode(false); // Turn off demo mode on logout
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const loadRecentPayments = async () => {
    try {
      const payments = await fetchRecentPayments(20, demoMode); // Pass demoMode
      setRecentPayments(payments);
      
      // Calculate stats
      const total = payments.length;
      const volume = payments.reduce((sum, p) => sum + (p.amount_usd || 0), 0);
      const success = payments.filter(p => p.status === 'completed').length;
      
      setStats({ total, volume: volume.toFixed(2), success });
    } catch (error) {
      console.error('Failed to load payments:', error);
    }
  };

  // Show login if not authenticated
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={() => {
      console.log('[APP] Login callback triggered, checking auth...');
      checkAuth();
    }} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <motion.nav 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div 
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <motion.div 
                className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <span className="text-white font-bold text-xl">₿</span>
              </motion.div>
              <h1 className="text-2xl font-bold text-gray-900">
                USDC Payment Gateway
              </h1>
            </motion.div>
            
            <div className="flex items-center space-x-4">
              <div className="flex space-x-2">
                <motion.button
                  onClick={() => navigate('/demo')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-4 py-2 rounded-lg font-medium transition bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-md"
                >
                  ▶️ Watch Live Demo
                </motion.button>
                <motion.button
                  onClick={() => setActiveTab('create')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    activeTab === 'create'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Create Payment
                </motion.button>
                <motion.button
                  onClick={() => setActiveTab('track')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    activeTab === 'track'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Track Payments
                </motion.button>
              </div>
              
              {/* Demo Mode Toggle */}
              <motion.button
                onClick={() => setDemoMode(!demoMode)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  demoMode
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                title={demoMode ? 'Demo mode active - viewing sample transactions' : 'Toggle demo mode to view sample transactions'}
              >
                {demoMode ? '🎭 Demo Mode ON' : '🎭 Demo Mode'}
              </motion.button>
              
              {/* User Menu */}
              <div className="flex items-center space-x-3 ml-auto">
                {/* User Avatar/Icon - Always show an icon */}
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  className="relative"
                >
                  {user.picture ? (
                    <img
                      src={user.picture}
                      alt={user.name || 'User'}
                      className="w-10 h-10 rounded-full border-2 border-indigo-500 object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg border-2 border-indigo-500 shadow-md">
                      {user.name ? user.name.charAt(0).toUpperCase() : user.email ? user.email.charAt(0).toUpperCase() : '👤'}
                    </div>
                  )}
                </motion.div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{user.name || 'User'}</p>
                  <p className="text-xs text-gray-500">{user.email || ''}</p>
                </div>
                <motion.button
                  onClick={handleLogout}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
                >
                  Logout
                </motion.button>
              </div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Stats Bar */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <motion.div 
            className="bg-white rounded-lg shadow p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 25px rgba(0,0,0,0.1)" }}
          >
            <p className="text-sm text-gray-600">Total Transactions</p>
            <motion.p 
              className="text-3xl font-bold text-gray-900"
              key={stats.total}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
            >
              {stats.total}
            </motion.p>
          </motion.div>
          <motion.div 
            className="bg-white rounded-lg shadow p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 25px rgba(0,0,0,0.1)" }}
          >
            <p className="text-sm text-gray-600">Volume Processed</p>
            <motion.p 
              className="text-3xl font-bold text-gray-900"
              key={stats.volume}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
            >
              ${stats.volume}
            </motion.p>
          </motion.div>
          <motion.div 
            className="bg-white rounded-lg shadow p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 25px rgba(0,0,0,0.1)" }}
          >
            <p className="text-sm text-gray-600">Success Rate</p>
            <motion.p 
              className="text-3xl font-bold text-gray-900"
              key={stats.total > 0 ? ((stats.success / stats.total) * 100).toFixed(1) : 0}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
            >
              {stats.total > 0 ? ((stats.success / stats.total) * 100).toFixed(1) : 0}%
            </motion.p>
          </motion.div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <AnimatePresence mode="wait">
          {activeTab === 'create' ? (
            <motion.div
              key="create"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <PaymentForm onPaymentCreated={loadRecentPayments} demoMode={demoMode} />
            </motion.div>
          ) : (
            <motion.div
              key="track"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <TransactionTracker payments={recentPayments} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-gray-600">
        <p className="text-sm">
          Powered by Circle CCTP • Supporting 5+ Blockchains
        </p>
      </footer>
    </div>
  );
}

// Main App component with router wrapper
function App() {
  return (
    <Routes>
      <Route path="/demo" element={<LiveDemo />} />
      <Route path="/*" element={<AppContent />} />
    </Routes>
  );
}

export default App;
