import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ethers } from 'ethers';
import ChainSelector, { CHAINS } from './ChainSelector';
import { createPayment, initiateBurn } from '../utils/api';

// Token Messenger addresses (simplified - in production, fetch from chain config)
const TOKEN_MESSENGER_ADDRESSES = {
  sepolia: '0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5',
  base_sepolia: '0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5',
  avalanche_fuji: '0xeb08f243e5d3fcff26a9e38ae5520a669f4019d0',
  polygon_amoy: '0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5',
  arbitrum_sepolia: '0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5'
};

// Domain IDs for CCTP
const DOMAIN_IDS = {
  sepolia: 0,
  base_sepolia: 6,
  avalanche_fuji: 1,
  polygon_amoy: 7,
  arbitrum_sepolia: 3
};

function PaymentForm({ onPaymentCreated }) {
  const [formData, setFormData] = useState({
    amount: '',
    sourceChain: 'sepolia',
    destChain: 'base_sepolia',
    recipientAddress: ''
  });
  
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState('');

  // Connect wallet using MetaMask
  const connectWallet = async () => {
    if (!window.ethereum) {
      alert('Please install MetaMask to use this feature');
      return;
    }

    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const accounts = await provider.send('eth_requestAccounts', []);
      setWalletAddress(accounts[0]);
      setWalletConnected(true);
    } catch (error) {
      console.error('Wallet connection failed:', error);
      alert('Failed to connect wallet');
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!walletConnected) {
      alert('Please connect your wallet first');
      return;
    }

    setProcessing(true);
    setStatus('Creating payment request...');

    try {
      // Step 1: Create payment in backend
      const payment = await createPayment({
        amount: parseFloat(formData.amount),
        source_chain: formData.sourceChain,
        dest_chain: formData.destChain,
        sender_address: walletAddress,
        recipient_address: formData.recipientAddress
      });

      setStatus('Switching to source chain...');

      // Step 2: Switch to source chain
      const provider = new ethers.BrowserProvider(window.ethereum);
      const currentChainId = await provider.send('eth_chainId', []);
      const targetChainId = CHAINS[formData.sourceChain].chainId;

      if (currentChainId !== targetChainId) {
        try {
          await provider.send('wallet_switchEthereumChain', [
            { chainId: targetChainId }
          ]);
        } catch (switchError) {
          // If chain doesn't exist, try to add it
          if (switchError.code === 4902) {
          // For now, just show error - in production, add chain configuration
            throw new Error(`Please add ${CHAINS[formData.sourceChain].name} to MetaMask`);
          }
          throw switchError;
        }
      }

      setStatus('Approving USDC spend...');

      // Step 3: Approve USDC spend
      const signer = await provider.getSigner();
      const usdcAddress = CHAINS[formData.sourceChain].usdcAddress;
      
      // USDC ABI
      const usdcAbi = [
        'function approve(address spender, uint256 amount) returns (bool)',
        'function balanceOf(address account) view returns (uint256)'
      ];
      
      const usdc = new ethers.Contract(usdcAddress, usdcAbi, signer);
      const amountInSmallestUnit = ethers.parseUnits(formData.amount, 6);
      
      // Check balance first
      const balance = await usdc.balanceOf(walletAddress);
      if (balance < amountInSmallestUnit) {
        throw new Error(`Insufficient USDC balance. Have: ${ethers.formatUnits(balance, 6)}, Need: ${formData.amount}`);
      }
      
      // Approve TokenMessenger
      const tokenMessengerAddress = TOKEN_MESSENGER_ADDRESSES[formData.sourceChain];
      const approveTx = await usdc.approve(tokenMessengerAddress, amountInSmallestUnit);
      await approveTx.wait();

      setStatus('Burning USDC on source chain...');

      // Step 4: Call depositForBurn
      const tokenMessengerAbi = [
        'function depositForBurn(uint256 amount, uint32 destinationDomain, bytes32 mintRecipient, address burnToken) returns (uint64)'
      ];
      
      const tokenMessenger = new ethers.Contract(tokenMessengerAddress, tokenMessengerAbi, signer);
      
      // Convert recipient address to bytes32 (pad with zeros)
      const recipientBytes32 = ethers.zeroPadValue(formData.recipientAddress, 32);
      const destinationDomain = DOMAIN_IDS[formData.destChain];
      
      const burnTx = await tokenMessenger.depositForBurn(
        amountInSmallestUnit,
        destinationDomain,
        recipientBytes32,
        usdcAddress
      );
      
      const burnReceipt = await burnTx.wait();
      const burnTxHash = burnReceipt.hash;

      setStatus('Notifying backend...');

      // Step 5: Notify backend of burn
      await initiateBurn({
        payment_id: payment.payment_id,
        burn_tx_hash: burnTxHash
      });

      setStatus(`Transfer initiated! Payment ID: ${payment.payment_id}. Check "Track Payments" tab for updates.`);
      
      // Reset form
      setFormData({
        amount: '',
        sourceChain: 'sepolia',
        destChain: 'base_sepolia',
        recipientAddress: ''
      });

      // Notify parent to refresh
      if (onPaymentCreated) onPaymentCreated();

    } catch (error) {
      console.error('Payment failed:', error);
      setStatus('Payment failed: ' + error.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <motion.div 
      className="bg-black/60 backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <motion.h2 
        className="text-2xl font-bold text-white mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        Create Cross-Chain Payment
      </motion.h2>

      {/* Wallet Connection */}
      <AnimatePresence mode="wait">
        {!walletConnected ? (
          <motion.button
            key="connect"
            onClick={connectWallet}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="w-full bg-white text-black py-3 rounded-lg font-medium hover:bg-white/90 transition mb-6 border border-white/20"
          >
            Connect Wallet
          </motion.button>
        ) : (
          <motion.div 
            key="connected"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="mb-6 p-4 bg-white/10 border border-white/30 rounded-lg"
          >
            <p className="text-sm text-white/90">
              Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Payment Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Amount */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <label className="block text-sm font-medium text-white/80 mb-2">
            Amount (USDC)
          </label>
          <motion.input
            type="number"
            step="0.01"
            min="0.01"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            whileFocus={{ scale: 1.02 }}
            className="w-full px-4 py-2 bg-black/40 border border-white/30 rounded-lg focus:ring-2 focus:ring-white/50 text-white placeholder-white/50"
            placeholder="10.00"
            required
          />
        </motion.div>

        {/* Source Chain */}
        <ChainSelector
          value={formData.sourceChain}
          onChange={(value) => setFormData({ ...formData, sourceChain: value })}
          label="Source Chain (Pay From)"
        />

        {/* Destination Chain */}
        <ChainSelector
          value={formData.destChain}
          onChange={(value) => setFormData({ ...formData, destChain: value })}
          label="Destination Chain (Receive On)"
        />

        {/* Recipient Address */}
        <div>
          <label className="block text-sm font-medium text-white/80 mb-2">
            Recipient Address
          </label>
          <input
            type="text"
            value={formData.recipientAddress}
            onChange={(e) => setFormData({ ...formData, recipientAddress: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
            placeholder="0x..."
            required
          />
        </div>

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={processing || !walletConnected}
          whileHover={!processing && walletConnected ? { scale: 1.02 } : {}}
          whileTap={!processing && walletConnected ? { scale: 0.98 } : {}}
          className="w-full bg-white text-black py-3 rounded-lg font-medium hover:bg-white/90 disabled:bg-white/20 disabled:cursor-not-allowed transition border border-white/20"
        >
          {processing ? (
            <span className="flex items-center justify-center">
              <motion.span
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="inline-block mr-2"
              >
                ⏳
              </motion.span>
              Processing...
            </span>
          ) : (
            'Initiate Payment'
          )}
        </motion.button>

        {/* Status Message */}
        <AnimatePresence>
          {status && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-4 bg-white/10 border border-white/30 rounded-lg"
            >
              <p className="text-sm text-white/90">{status}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </form>
    </motion.div>
  );
}

export default PaymentForm;

