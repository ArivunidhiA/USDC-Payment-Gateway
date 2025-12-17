"""
Chain configurations for CCTP-supported testnets.

Each chain has its own USDC contract and domain ID for cross-chain transfers.
"""

CHAINS = {
    "sepolia": {
        "chain_id": 11155111,
        "name": "Ethereum Sepolia",
        "rpc_url": "https://eth-sepolia.g.alchemy.com/v2/demo",
        "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
        "token_messenger": "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5",
        "message_transmitter": "0x7865fAfC2db2093669d92c0F33AeEF291086BEFD",
        "domain": 0,  # CCTP domain ID
        "explorer": "https://sepolia.etherscan.io/tx/"
    },
    "base_sepolia": {
        "chain_id": 84532,
        "name": "Base Sepolia",
        "rpc_url": "https://sepolia.base.org",
        "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        "token_messenger": "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5",
        "message_transmitter": "0x7865fAfC2db2093669d92c0F33AeEF291086BEFD",
        "domain": 6,
        "explorer": "https://sepolia.basescan.org/tx/"
    },
    "avalanche_fuji": {
        "chain_id": 43113,
        "name": "Avalanche Fuji",
        "rpc_url": "https://api.avax-test.network/ext/bc/C/rpc",
        "usdc_address": "0x5425890298aed601595a70AB815c96711a31Bc65",
        "token_messenger": "0xeb08f243e5d3fcff26a9e38ae5520a669f4019d0",
        "message_transmitter": "0xa9fb1b3009dcb79e2fe346c16a604b8fa8ae0a79",
        "domain": 1,
        "explorer": "https://testnet.snowtrace.io/tx/"
    },
    "polygon_amoy": {
        "chain_id": 80002,
        "name": "Polygon Amoy",
        "rpc_url": "https://rpc-amoy.polygon.technology",
        "usdc_address": "0x41e94eb019c0762f9bfcf9fb1e58725bfb0e7582",
        "token_messenger": "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5",
        "message_transmitter": "0x7865fAfC2db2093669d92c0F33AeEF291086BEFD",
        "domain": 7,
        "explorer": "https://amoy.polygonscan.com/tx/"
    },
    "arbitrum_sepolia": {
        "chain_id": 421614,
        "name": "Arbitrum Sepolia",
        "rpc_url": "https://sepolia-rollup.arbitrum.io/rpc",
        "usdc_address": "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d",
        "token_messenger": "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5",
        "message_transmitter": "0xaCF1ceeF35caAc005e15888dDb8A3515C41B4872",
        "domain": 3,
        "explorer": "https://sepolia.arbiscan.io/tx/"
    }
}


def get_chain_config(chain_name):
    """Fetch configuration for a specific chain."""
    if chain_name not in CHAINS:
        raise ValueError(f"Unsupported chain: {chain_name}")
    return CHAINS[chain_name]


def get_all_chains():
    """Return list of supported chain names."""
    return list(CHAINS.keys())

