import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { checkPaymentStatus } from '../utils/api';
import { CHAINS } from './ChainSelector';

function TransactionTracker({ payments }) {
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Poll selected payment for updates
  useEffect(() => {
    if (!selectedPayment) return;

    const interval = setInterval(async () => {
      try {
        const updated = await checkPaymentStatus(selectedPayment.payment_id);
        setSelectedPayment(updated);
      } catch (error) {
        console.error('Failed to refresh payment:', error);
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [selectedPayment]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'pending':
      case 'burning':
      case 'fetching_attestation':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getExplorerUrl = (chain, txHash) => {
    const explorers = {
      sepolia: 'https://sepolia.etherscan.io/tx/',
      base_sepolia: 'https://sepolia.basescan.org/tx/',
      avalanche_fuji: 'https://testnet.snowtrace.io/tx/',
      polygon_amoy: 'https://amoy.polygonscan.com/tx/',
      arbitrum_sepolia: 'https://sepolia.arbiscan.io/tx/'
    };
    return explorers[chain] ? `${explorers[chain]}${txHash}` : '#';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Payments List */}
      <motion.div 
        className="bg-white rounded-lg shadow-lg p-6"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Recent Payments
        </h2>
        
        <div className="space-y-3 max-h-96 overflow-y-auto">
          <AnimatePresence mode="wait">
            {!payments || payments.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="text-center py-12"
              >
                <motion.div
                  animate={{ 
                    scale: [1, 1.1, 1],
                    rotate: [0, 5, -5, 0]
                  }}
                  transition={{ 
                    duration: 2,
                    repeat: Infinity,
                    repeatDelay: 1
                  }}
                  className="text-6xl mb-4"
                >
                  💸
                </motion.div>
                <p className="text-gray-500 text-lg font-medium mb-2">
                  No payments yet
                </p>
                <p className="text-gray-400 text-sm">
                  Create your first cross-chain payment to get started!
                </p>
              </motion.div>
            ) : (
              payments.map((payment, index) => (
                <motion.div
                  key={payment.payment_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => setSelectedPayment(payment)}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-4 border rounded-lg cursor-pointer transition ${
                    selectedPayment?.payment_id === payment.payment_id
                      ? 'border-indigo-500 bg-indigo-50 shadow-md'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">
                        ${payment.amount_usd}
                      </p>
                      <p className="text-sm text-gray-600">
                        {payment.source_chain} → {payment.dest_chain}
                      </p>
                    </div>
                    <motion.span
                      className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                        payment.status
                      )}`}
                      whileHover={{ scale: 1.1 }}
                    >
                      {payment.status}
                    </motion.span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(payment.created_at).toLocaleString()}
                  </p>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Payment Details */}
      <motion.div 
        className="bg-white rounded-lg shadow-lg p-6"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Payment Details
        </h2>

        <AnimatePresence mode="wait">
          {!selectedPayment ? (
            <motion.div
              key="no-selection"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="text-center py-12"
            >
              <motion.div
                animate={{ 
                  y: [0, -10, 0],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  repeatDelay: 0.5
                }}
                className="text-5xl mb-4"
              >
                👆
              </motion.div>
              <p className="text-gray-500 text-lg font-medium mb-2">
                Select a payment
              </p>
              <p className="text-gray-400 text-sm">
                Choose a payment from the list to view details
              </p>
            </motion.div>
          ) : (
            <motion.div
              key={selectedPayment.payment_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
            {/* Status Timeline */}
            <div className="border-l-4 border-indigo-500 pl-4 space-y-4">
              <motion.div 
                className="flex items-start space-x-3"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <motion.div 
                  className="flex-shrink-0 w-3 h-3 bg-green-500 rounded-full mt-1"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                ></motion.div>
                <div>
                  <p className="font-medium text-gray-900">Payment Created</p>
                  <p className="text-sm text-gray-600">
                    {new Date(selectedPayment.created_at).toLocaleString()}
                  </p>
                </div>
              </motion.div>

              <AnimatePresence>
                {selectedPayment.burn_tx_hash && (
                  <motion.div 
                    className="flex items-start space-x-3"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <motion.div 
                      className="flex-shrink-0 w-3 h-3 bg-green-500 rounded-full mt-1"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    ></motion.div>
                    <div>
                      <p className="font-medium text-gray-900">USDC Burned</p>
                      <motion.a
                        href={getExplorerUrl(selectedPayment.source_chain, selectedPayment.burn_tx_hash)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-indigo-600 hover:underline"
                        whileHover={{ scale: 1.05 }}
                      >
                        View Transaction ↗
                      </motion.a>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {selectedPayment.status === 'fetching_attestation' && (
                  <motion.div 
                    className="flex items-start space-x-3"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <motion.div 
                      className="flex-shrink-0 w-3 h-3 bg-yellow-500 rounded-full mt-1"
                      animate={{ 
                        scale: [1, 1.3, 1],
                        opacity: [1, 0.7, 1]
                      }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    ></motion.div>
                    <div>
                      <p className="font-medium text-gray-900">
                        Fetching Attestation
                      </p>
                      <p className="text-sm text-gray-600">
                        Waiting for Circle confirmation...
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {selectedPayment.mint_tx_hash && (
                  <motion.div 
                    className="flex items-start space-x-3"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ delay: 0.4 }}
                  >
                    <motion.div 
                      className="flex-shrink-0 w-3 h-3 bg-green-500 rounded-full mt-1"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    ></motion.div>
                    <div>
                      <p className="font-medium text-gray-900">USDC Minted</p>
                      <motion.a
                        href={getExplorerUrl(selectedPayment.dest_chain, selectedPayment.mint_tx_hash)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-indigo-600 hover:underline"
                        whileHover={{ scale: 1.05 }}
                      >
                        View Transaction ↗
                      </motion.a>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Payment Info */}
            <div className="border-t pt-4 mt-4">
              <h3 className="font-medium text-gray-900 mb-3">
                Payment Information
              </h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-600">Amount:</dt>
                  <dd className="font-medium">${selectedPayment.amount_usd}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">From:</dt>
                  <dd className="font-mono text-xs">
                    {selectedPayment.sender_address?.slice(0, 10)}...
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">To:</dt>
                  <dd className="font-mono text-xs">
                    {selectedPayment.recipient_address?.slice(0, 10)}...
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Payment ID:</dt>
                  <dd className="font-mono text-xs">
                    {selectedPayment.payment_id?.slice(0, 16)}...
                  </dd>
                </div>
              </dl>
            </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default TransactionTracker;

