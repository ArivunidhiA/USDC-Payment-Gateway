import React from 'react';

const CHAINS = {
  sepolia: {
    name: 'Ethereum Sepolia',
    chainId: '0xaa36a7',
    usdcAddress: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238'
  },
  base_sepolia: {
    name: 'Base Sepolia',
    chainId: '0x14a34',
    usdcAddress: '0x036CbD53842c5426634e7929541eC2318f3dCF7e'
  },
  avalanche_fuji: {
    name: 'Avalanche Fuji',
    chainId: '0xa869',
    usdcAddress: '0x5425890298aed601595a70AB815c96711a31Bc65'
  },
  polygon_amoy: {
    name: 'Polygon Amoy',
    chainId: '0x13882',
    usdcAddress: '0x41e94eb019c0762f9bfcf9fb1e58725bfb0e7582'
  },
  arbitrum_sepolia: {
    name: 'Arbitrum Sepolia',
    chainId: '0x66eee',
    usdcAddress: '0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d'
  }
};

function ChainSelector({ value, onChange, label }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
      >
        {Object.entries(CHAINS).map(([key, chain]) => (
          <option key={key} value={key}>
            {chain.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ChainSelector;
export { CHAINS };

