import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import PaymentForm from './components/PaymentForm';
import TransactionTracker from './components/TransactionTracker';
import Login from './components/Login';
import LiveDemo from './components/LiveDemo';
import { WaveBackground } from './components/ui/WaveBackground';
import { fetchRecentPayments, getCurrentUser, logout } from './utils/api';

function AppContent() {
  const [activeTab, setActiveTab] = useState('create'); // 'create' or 'track'
  const [recentPayments, setRecentPayments] = useState([]);
  const [stats, setStats] = useState({ total: 0, volume: 0, success: 0 });
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Load recent payments when authenticated
  useEffect(() => {
    if (user) {
      loadRecentPayments();
    } else {
      setRecentPayments([]);
      setStats({ total: 0, volume: 0, success: 0 });
    }
  }, [user]);

  const checkAuth = async () => {
    try {
      const currentUser = await getCurrentUser();
      if (currentUser && currentUser.user_id) {
        setUser(currentUser);
      } else {
        setUser(null);
        setLoading(false); // Ensure loading is false when no user
      }
    } catch (error) {
      console.log('Auth check failed:', error);
      setUser(null);
      setLoading(false); // Ensure loading is false on error
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
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const loadRecentPayments = async () => {
    try {
      const payments = await fetchRecentPayments(20);
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
      <div className="min-h-screen bg-black text-white relative flex items-center justify-center">
        <WaveBackground 
          strokeColor="#ffffff"
          backgroundColor="#000000"
          opacity={0.5}
          className="fixed inset-0"
        />
        <div className="relative z-10">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-12 h-12 border-4 border-white border-t-transparent rounded-full"
          />
        </div>
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
    <div className="min-h-screen bg-black text-white relative">
      {/* Wave Background with 50% opacity */}
      <WaveBackground 
        strokeColor="#ffffff"
        backgroundColor="#000000"
        opacity={0.5}
        className="fixed inset-0"
      />
      
      {/* Content with higher z-index */}
      <div className="relative z-10">
      {/* Header */}
      <motion.nav 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-black/80 backdrop-blur-sm border-b border-white/20 shadow-lg"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div 
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <motion.div 
                className="w-10 h-10 bg-white rounded-lg flex items-center justify-center"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <span className="text-black font-bold text-xl">₿</span>
              </motion.div>
              <h1 className="text-2xl font-bold text-white">
                USDC Payment Gateway
              </h1>
            </motion.div>
            
            <div className="flex items-center space-x-4">
              <div className="flex space-x-2">
                <motion.button
                  onClick={() => navigate('/demo')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-4 py-2 rounded-lg font-medium transition bg-white text-black hover:bg-white/90 shadow-lg border border-white/20"
                >
                  ▶️ Watch Live Demo
                </motion.button>
                <motion.button
                  onClick={() => setActiveTab('create')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-4 py-2 rounded-lg font-medium transition border ${
                    activeTab === 'create'
                      ? 'bg-white text-black border-white'
                      : 'bg-transparent text-white border-white/30 hover:border-white/50'
                  }`}
                >
                  Create Payment
                </motion.button>
                <motion.button
                  onClick={() => setActiveTab('track')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-4 py-2 rounded-lg font-medium transition border ${
                    activeTab === 'track'
                      ? 'bg-white text-black border-white'
                      : 'bg-transparent text-white border-white/30 hover:border-white/50'
                  }`}
                >
                  Track Payments
                </motion.button>
              </div>
              
              {/* User Menu */}
              <div className="flex items-center space-x-3 ml-auto">
                {/* User Avatar/Icon - Always show an icon */}
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  className="relative"
                >
                  {user.picture && user.picture.trim() !== '' ? (
                    <img
                      src={user.picture}
                      alt={user.name || 'User'}
                      className="w-10 h-10 rounded-full border-2 border-white object-cover"
                      onError={(e) => {
                        // If image fails to load, hide image and show fallback
                        e.target.style.display = 'none';
                        const fallback = e.target.parentElement.querySelector('.avatar-fallback');
                        if (fallback) fallback.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div 
                    className={`avatar-fallback w-10 h-10 rounded-full bg-white flex items-center justify-center text-black font-bold text-lg border-2 border-white shadow-md ${user.picture && user.picture.trim() !== '' ? 'hidden' : ''}`}
                  >
                    {user.name ? user.name.charAt(0).toUpperCase() : user.email ? user.email.charAt(0).toUpperCase() : '👤'}
                  </div>
                </motion.div>
                <div className="text-right">
                  <p className="text-sm font-medium text-white">{user.name || 'User'}</p>
                  <p className="text-xs text-white/70">{user.email || ''}</p>
                </div>
                <motion.button
                  onClick={handleLogout}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-3 py-1 text-sm text-white/80 hover:text-white border border-white/30 hover:border-white/50 rounded-lg transition"
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
            className="bg-black/60 backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 25px rgba(255,255,255,0.1)" }}
          >
            <p className="text-sm text-white/70">Total Transactions</p>
            <motion.p 
              className="text-3xl font-bold text-white"
              key={stats.total}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
            >
              {stats.total}
            </motion.p>
          </motion.div>
          <motion.div 
            className="bg-black/60 backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 25px rgba(255,255,255,0.1)" }}
          >
            <p className="text-sm text-white/70">Volume Processed</p>
            <motion.p 
              className="text-3xl font-bold text-white"
              key={stats.volume}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
            >
              ${stats.volume}
            </motion.p>
          </motion.div>
          <motion.div 
            className="bg-black/60 backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 25px rgba(255,255,255,0.1)" }}
          >
            <p className="text-sm text-white/70">Success Rate</p>
            <motion.p 
              className="text-3xl font-bold text-white"
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
              <PaymentForm onPaymentCreated={loadRecentPayments} />
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
      <footer className="mt-12 py-6 text-center text-white/70">
        <p className="text-sm">
          Powered by Circle CCTP • Supporting 5+ Blockchains
        </p>
      </footer>
      </div>
    </div>
  );
}

// Protected route wrapper for authenticated routes
function ProtectedRoute({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const currentUser = await getCurrentUser();
      if (currentUser && currentUser.user_id) {
        setUser(currentUser);
      } else {
        setUser(null);
        // Redirect to login if not authenticated
        navigate('/');
      }
    } catch (error) {
      console.log('Auth check failed:', error);
      setUser(null);
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white relative flex items-center justify-center">
        <WaveBackground 
          strokeColor="#ffffff"
          backgroundColor="#000000"
          opacity={0.5}
          className="fixed inset-0"
        />
        <div className="relative z-10">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-12 h-12 border-4 border-white border-t-transparent rounded-full"
          />
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return children;
}

// Main App component with router wrapper
function App() {
  return (
    <Routes>
      <Route path="/" element={<Login onLogin={() => window.location.reload()} />} />
      <Route path="/app" element={<ProtectedRoute><AppContent /></ProtectedRoute>} />
      <Route path="/demo" element={<ProtectedRoute><LiveDemo /></ProtectedRoute>} />
    </Routes>
  );
}

export default App;
