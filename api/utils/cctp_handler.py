"""
Handles Circle CCTP operations: burning USDC on source chain,
fetching attestations, and minting on destination chain.
"""

import time
import os
import base64
import requests
from web3 import Web3
from eth_account import Account
from .chain_config import get_chain_config

# ABI snippets for USDC and CCTP contracts
USDC_ABI = [
    {
        "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

TOKEN_MESSENGER_ABI = [
    {
        "inputs": [
            {"name": "amount", "type": "uint256"},
            {"name": "destinationDomain", "type": "uint32"},
            {"name": "mintRecipient", "type": "bytes32"},
            {"name": "burnToken", "type": "address"}
        ],
        "name": "depositForBurn",
        "outputs": [{"name": "nonce", "type": "uint64"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

MESSAGE_TRANSMITTER_ABI = [
    {
        "inputs": [
            {"name": "message", "type": "bytes"},
            {"name": "attestation", "type": "bytes"}
        ],
        "name": "receiveMessage",
        "outputs": [{"name": "success", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

class CCTPHandler:
    """Manages cross-chain USDC transfers via Circle's CCTP."""
    
    def __init__(self, source_chain, dest_chain):
        self.source_config = get_chain_config(source_chain)
        self.dest_config = get_chain_config(dest_chain)
        self.source_web3 = Web3(Web3.HTTPProvider(self.source_config["rpc_url"]))
        self.dest_web3 = Web3(Web3.HTTPProvider(self.dest_config["rpc_url"]))
        
        # Use production API if key is provided, otherwise use sandbox
        self.CIRCLE_API_KEY = os.getenv('CIRCLE_API_KEY')
        if self.CIRCLE_API_KEY:
            self.ATTESTATION_API = "https://iris-api.circle.com/v1/attestations"
        else:
            self.ATTESTATION_API = "https://iris-api-sandbox.circle.com/v1/attestations"
    
    def burn_usdc(self, sender_address, private_key, amount_usdc, recipient_address):
        """
        Step 1: Approve and burn USDC on source chain.
        Returns transaction hash of the burn.
        """
        # Convert USDC amount to smallest unit (6 decimals)
        amount_raw = int(amount_usdc * 1_000_000)
        
        # Setup contracts
        usdc = self.source_web3.eth.contract(
            address=Web3.to_checksum_address(self.source_config["usdc_address"]),
            abi=USDC_ABI
        )
        
        messenger = self.source_web3.eth.contract(
            address=Web3.to_checksum_address(self.source_config["token_messenger"]),
            abi=TOKEN_MESSENGER_ABI
        )
        
        # Check balance
        balance = usdc.functions.balanceOf(sender_address).call()
        if balance < amount_raw:
            raise ValueError(f"Insufficient balance. Have: {balance/1e6} USDC, Need: {amount_usdc} USDC")
        
        # Approve token messenger to spend USDC
        account = Account.from_key(private_key)
        nonce = self.source_web3.eth.get_transaction_count(sender_address)
        
        approve_tx = usdc.functions.approve(
            self.source_config["token_messenger"],
            amount_raw
        ).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': self.source_web3.eth.gas_price
        })
        
        signed_approve = self.source_web3.eth.account.sign_transaction(approve_tx, private_key)
        approve_hash = self.source_web3.eth.send_raw_transaction(signed_approve.rawTransaction)
        
        # Wait for approval confirmation
        self.source_web3.eth.wait_for_transaction_receipt(approve_hash, timeout=120)
        
        # Burn USDC via depositForBurn
        # Convert recipient address to bytes32 format required by CCTP
        recipient_bytes32 = b'\x00' * 12 + bytes.fromhex(recipient_address[2:])
        
        burn_tx = messenger.functions.depositForBurn(
            amount_raw,
            self.dest_config["domain"],
            recipient_bytes32,
            self.source_config["usdc_address"]
        ).build_transaction({
            'from': sender_address,
            'nonce': nonce + 1,
            'gas': 200000,
            'gasPrice': self.source_web3.eth.gas_price
        })
        
        signed_burn = self.source_web3.eth.account.sign_transaction(burn_tx, private_key)
        burn_hash = self.source_web3.eth.send_raw_transaction(signed_burn.rawTransaction)
        
        return burn_hash.hex()
    
    def fetch_attestation(self, burn_tx_hash, max_wait=300):
        """
        Step 2: Poll Circle's API for attestation signature.
        This proves the burn happened and allows minting on destination.
        
        Note: The message hash can be extracted from the MessageSent event
        emitted by the MessageTransmitter contract. The event signature is:
        keccak256("MessageSent(bytes)")
        """
        # Get transaction receipt to extract message hash
        receipt = self.source_web3.eth.wait_for_transaction_receipt(burn_tx_hash, timeout=120)
        
        # MessageSent event signature: keccak256("MessageSent(bytes)")
        # This is the actual event signature from MessageTransmitter contract
        message_sent_topic = Web3.keccak(text="MessageSent(bytes)").hex()
        
        # Extract MessageSent event from logs
        message_hash = None
        for log in receipt['logs']:
            # Check if this log is from the MessageTransmitter contract
            if (log['address'].lower() == self.source_config["message_transmitter"].lower() and
                len(log['topics']) > 0 and
                log['topics'][0].hex() == message_sent_topic):
                # The message hash is in the data field (not topics)
                # For MessageSent(bytes), the data contains the message bytes
                # We need to hash the message to get the message hash
                if log.get('data') and log['data'] != '0x':
                    message_bytes = bytes.fromhex(log['data'][2:])
                    # The message hash is keccak256 of the message
                    message_hash = Web3.keccak(message_bytes).hex()
                    break
        
        # Alternative: If we can't extract from logs, try using Circle's transaction lookup
        # This is a fallback method
        if not message_hash:
            # Try to get message hash from Circle API using transaction hash
            # Note: This endpoint may not exist, but it's worth trying
            try:
                response = requests.get(f"{self.ATTESTATION_API.replace('/v1/attestations', '')}/v1/messages", 
                                      params={'txHash': burn_tx_hash})
                if response.status_code == 200:
                    data = response.json()
                    if data.get('messages') and len(data['messages']) > 0:
                        message_hash = data['messages'][0].get('messageHash')
            except:
                pass
        
        if not message_hash:
            # Last resort: construct message hash from transaction data
            # This is not ideal but may work in some cases
            raise ValueError("Could not extract message hash from burn transaction. Please check transaction logs manually.")
        
        # Poll Circle API for attestation
        start_time = time.time()
        headers = {}
        if self.CIRCLE_API_KEY:
            # Circle API uses Basic Auth with format: API_KEY:API_SECRET
            # The key format is: API_KEY:API_SECRET
            auth_string = base64.b64encode(self.CIRCLE_API_KEY.encode()).decode()
            headers['Authorization'] = f'Basic {auth_string}'
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.ATTESTATION_API}/{message_hash}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'complete':
                        return {
                            'attestation': data['attestation'],
                            'message': data['message'],
                            'message_hash': message_hash
                        }
                    elif data.get('status') == 'pending':
                        # Still waiting for attestation
                        pass
                    else:
                        # Error or unknown status
                        raise ValueError(f"Attestation status: {data.get('status')}")
            except requests.exceptions.RequestException as e:
                # Log error but continue polling
                print(f"Error fetching attestation: {e}")
            
            time.sleep(3)  # Wait 3 seconds before retry
        
        raise TimeoutError("Attestation not available within timeout period")
    
    def mint_usdc(self, attestation_data, recipient_private_key):
        """
        Step 3: Use attestation to mint USDC on destination chain.
        Returns transaction hash of the mint.
        """
        transmitter = self.dest_web3.eth.contract(
            address=Web3.to_checksum_address(self.dest_config["message_transmitter"]),
            abi=MESSAGE_TRANSMITTER_ABI
        )
        
        account = Account.from_key(recipient_private_key)
        recipient_address = account.address
        
        # Build mint transaction
        nonce = self.dest_web3.eth.get_transaction_count(recipient_address)
        
        mint_tx = transmitter.functions.receiveMessage(
            bytes.fromhex(attestation_data['message'][2:]),  # Remove '0x' prefix
            bytes.fromhex(attestation_data['attestation'][2:])
        ).build_transaction({
            'from': recipient_address,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': self.dest_web3.eth.gas_price
        })
        
        signed_mint = self.dest_web3.eth.account.sign_transaction(mint_tx, recipient_private_key)
        mint_hash = self.dest_web3.eth.send_raw_transaction(signed_mint.rawTransaction)
        
        return mint_hash.hex()
    
    def get_tx_status(self, tx_hash, chain_type='source'):
        """Check transaction confirmation status."""
        web3 = self.source_web3 if chain_type == 'source' else self.dest_web3
        
        try:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            return {
                'confirmed': True,
                'success': receipt['status'] == 1,
                'block_number': receipt['blockNumber']
            }
        except Exception:
            return {'confirmed': False, 'success': False}

