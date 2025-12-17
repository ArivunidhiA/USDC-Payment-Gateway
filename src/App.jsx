import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Routes, Route, useNavigate } from 'react-router-dom';
import PaymentForm from './components/PaymentForm';
import TransactionTracker from './components/TransactionTracker';
import LiveDemo from './components/LiveDemo';
import { WaveBackground } from './components/ui/WaveBackground';
import { fetchRecentPayments } from './utils/api';

function AppContent() {
  const [activeTab, setActiveTab] = useState('create'); // 'create' or 'track'
  const [recentPayments, setRecentPayments] = useState([]);
  const [stats, setStats] = useState({ total: 0, volume: 0, success: 0 });
  const navigate = useNavigate();

  // Load recent payments on mount
  useEffect(() => {
    loadRecentPayments();
  }, []);

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
                  onClick={() => navigate('/')}
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

// Main App component with router wrapper
function App() {
  return (
    <Routes>
      <Route path="/" element={<LiveDemo />} />
      <Route path="/demo" element={<LiveDemo />} />
      <Route path="/app" element={<AppContent />} />
    </Routes>
  );
}

export default App;
