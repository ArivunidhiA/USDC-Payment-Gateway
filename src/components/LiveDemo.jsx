import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const DEMO_STAGES = [
  {
    id: 'created',
    title: 'Payment Created',
    status: 'completed',
    description: 'Payment request initialized',
    txHash: null,
    time: 0,
    icon: '✅'
  },
  {
    id: 'burning',
    title: 'USDC Burned on Ethereum',
    status: 'completed',
    description: 'Tokens burned on source chain',
    txHash: '0xabc123def456789abc123def456789abc123def456789abc123def4567891234',
    chain: 'Ethereum Sepolia',
    time: 5,
    icon: '🔥',
    explorerUrl: 'https://sepolia.etherscan.io/tx/0xabc123def456789abc123def456789abc123def456789abc123def4567891234'
  },
  {
    id: 'attestation',
    title: 'Circle Attestation',
    status: 'processing',
    description: 'Fetching attestation from Circle API',
    messageHash: '0x456789def0123456789def0123456789def0123456789def0123456789def0',
    time: 15,
    icon: '⏳',
    progress: 80
  },
  {
    id: 'minting',
    title: 'Minting on Base',
    status: 'processing',
    description: 'Attestation verified, minting USDC',
    estimatedTime: '30 seconds',
    time: 25,
    icon: '⏳',
    progress: 60
  },
  {
    id: 'completed',
    title: 'Transfer Completed',
    status: 'completed',
    description: 'USDC successfully minted on Base',
    txHash: '0x789def0123456789def0123456789def0123456789def0123456789def0123',
    chain: 'Base Sepolia',
    time: 35,
    icon: '✅',
    explorerUrl: 'https://sepolia.basescan.org/tx/0x789def0123456789def0123456789def0123456789def0123456789def0123'
  }
];

const MOCK_TRANSACTIONS = [
  { amount: 250, source: 'ETH', dest: 'Polygon', time: '28s', status: 'completed' },
  { amount: 1000, source: 'Base', dest: 'Arbitrum', time: '31s', status: 'completed' },
  { amount: 75, source: 'Arbitrum', dest: 'ETH', time: '26s', status: 'completed' },
  { amount: 500, source: 'Avalanche', dest: 'Base', time: '29s', status: 'completed' },
  { amount: 125, source: 'Polygon', dest: 'ETH', time: '27s', status: 'completed' }
];

function LiveDemo() {
  const [currentStage, setCurrentStage] = useState(0);
  const [isRunning, setIsRunning] = useState(true);
  const [elapsedTime, setElapsedTime] = useState(0);
  const intervalRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isRunning) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      return;
    }

    // Auto-advance through stages
    intervalRef.current = setInterval(() => {
      setElapsedTime(prev => {
        const newTime = prev + 1;
        
        // Find which stage we should be in based on elapsed time
        let targetStage = 0;
        for (let i = DEMO_STAGES.length - 1; i >= 0; i--) {
          if (newTime >= DEMO_STAGES[i].time) {
            targetStage = i;
            break;
          }
        }
        
        setCurrentStage(targetStage);
        
        // Loop back after completion (after 40 seconds)
        if (newTime >= 40) {
          return 0; // Reset time
        }
        
        return newTime;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning]);

  const handleRestart = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setElapsedTime(0);
    setCurrentStage(0);
    setIsRunning(true);
  };

  const currentStageData = DEMO_STAGES[currentStage];
  const completedStages = DEMO_STAGES.filter((_, index) => index <= currentStage && DEMO_STAGES[index].status === 'completed');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <motion.nav 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.button
              onClick={() => window.location.href = '/'}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 text-gray-700 hover:text-indigo-600"
            >
              <span>←</span>
              <span>Back to App</span>
            </motion.button>
            <motion.div
              className="flex items-center space-x-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <span className="text-sm text-gray-600">🎬 Live Demo</span>
              <motion.button
                onClick={() => setIsRunning(!isRunning)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium"
              >
                {isRunning ? '⏸ Pause' : '▶ Resume'}
              </motion.button>
              <motion.button
                onClick={handleRestart}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium"
              >
                🔄 Restart
              </motion.button>
            </motion.div>
          </div>
        </div>
      </motion.nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Demo Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🎬 Live Demo: Cross-Chain Transfer
          </h1>
          <p className="text-lg text-gray-600">
            Auto-playing demonstration • No wallet needed
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Simulating $150 USDC transfer from Ethereum Sepolia → Base Sepolia
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Payment Request Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-lg shadow-lg p-6 border-2 border-indigo-200"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-4">Payment Request</h3>
            <div className="space-y-3">
              <div>
                <p className="text-3xl font-bold text-indigo-600">$150</p>
                <p className="text-sm text-gray-600">USDC</p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  ETH Sepolia
                </span>
                <span className="text-gray-400">→</span>
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                  Base Sepolia
                </span>
              </div>
            </div>
          </motion.div>

          {/* CCTP Processing Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg shadow-lg p-6 border-2 border-purple-200"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-4">CCTP Processing</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">{currentStageData.title}</span>
                  <span className="text-gray-500">{currentStageData.progress || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <motion.div
                    className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${currentStageData.progress || (currentStage / DEMO_STAGES.length) * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>
              <p className="text-sm text-gray-600">{currentStageData.description}</p>
            </div>
          </motion.div>

          {/* Status Timeline */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-4">Status Timeline</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {DEMO_STAGES.map((stage, index) => {
                const isActive = index === currentStage;
                const isCompleted = index < currentStage || (isActive && stage.status === 'completed');
                const isPending = index > currentStage;

                return (
                  <motion.div
                    key={stage.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`border-l-4 pl-4 pb-4 ${
                      isCompleted ? 'border-green-500' : isActive ? 'border-yellow-500' : 'border-gray-300'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      <span className="text-xl">{stage.icon}</span>
                      <div className="flex-1">
                        <p className={`font-medium ${isCompleted ? 'text-green-700' : isActive ? 'text-yellow-700' : 'text-gray-500'}`}>
                          {stage.title}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">{stage.description}</p>
                        {stage.txHash && (
                          <motion.a
                            href={stage.explorerUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-indigo-600 hover:underline mt-1 inline-block"
                            whileHover={{ scale: 1.05 }}
                          >
                            View on {stage.explorerUrl?.includes('etherscan') ? 'Etherscan' : 'BaseScan'} →
                          </motion.a>
                        )}
                        {stage.messageHash && (
                          <p className="text-xs text-gray-500 mt-1 font-mono">
                            Hash: {stage.messageHash.slice(0, 10)}...{stage.messageHash.slice(-8)}
                          </p>
                        )}
                        {stage.estimatedTime && (
                          <p className="text-xs text-gray-500 mt-1">
                            Estimated: {stage.estimatedTime}
                          </p>
                        )}
                        <p className="text-xs text-gray-400 mt-1">{stage.time}s</p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>

        {/* Recent Demo Transactions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Demo Transactions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {MOCK_TRANSACTIONS.map((tx, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-200"
              >
                <p className="text-lg font-bold text-indigo-600">${tx.amount}</p>
                <p className="text-sm text-gray-600 mt-1">{tx.source} → {tx.dest}</p>
                <div className="flex items-center space-x-2 mt-2">
                  <span className="text-green-500">✅</span>
                  <span className="text-xs text-gray-500">{tx.time}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 bg-indigo-50 border border-indigo-200 rounded-lg p-4"
        >
          <p className="text-sm text-indigo-800">
            <strong>💡 Note:</strong> This is an automated demonstration showing the CCTP (Cross-Chain Transfer Protocol) flow. 
            In production, each stage requires blockchain confirmations and Circle API attestation verification. 
            Actual transaction times may vary based on network conditions.
          </p>
        </motion.div>
      </div>
    </div>
  );
}

export default LiveDemo;

