# Development Notes

## Message Hash Extraction

The `fetch_attestation` method in `cctp_handler.py` extracts the message hash from the `MessageSent` event emitted by the TokenMessenger contract. The current implementation:

1. Looks for the `MessageSent(bytes)` event in transaction logs
2. Extracts the message bytes from the event data
3. Computes `keccak256(message_bytes)` to get the message hash
4. Uses this hash to query Circle's attestation API

**Note:** In production, you may need to:
- Use proper event ABI decoding for more reliable extraction
- Handle edge cases where the event structure differs between chains
- Add retry logic with exponential backoff for API calls

## Database

The application uses SQLite by default for development. For production:

1. Set `DATABASE_URL` environment variable to a PostgreSQL connection string
2. Update `db.py` to use `psycopg2` or `sqlalchemy` for PostgreSQL
3. Ensure proper connection pooling for serverless environments

## CCTP Contract Addresses

All contract addresses are configured in `chain_config.py`. These are testnet addresses. For mainnet:

1. Update all contract addresses to mainnet versions
2. Change RPC URLs to mainnet endpoints
3. Update domain IDs if they differ on mainnet
4. Use Circle's production attestation API (not sandbox)

## Frontend Wallet Integration

The frontend uses MetaMask via `ethers.js`. For production:

1. Add support for WalletConnect and other wallet providers
2. Implement proper error handling for rejected transactions
3. Add transaction status polling on the frontend
4. Show gas estimates before user confirms

## Security Considerations

1. **Private Keys:** Never store private keys in the backend. The current implementation assumes the frontend handles signing.
2. **API Keys:** Store sensitive keys in environment variables, never commit to git
3. **Input Validation:** All user inputs should be validated on both frontend and backend
4. **Rate Limiting:** Add rate limiting to API endpoints in production
5. **CORS:** Configure CORS properly for production domains only

## Deployment

### Vercel

The `vercel.json` configuration handles:
- Python serverless functions for `/api/*` routes
- Static build for React frontend
- Automatic routing

### Netlify

For Netlify deployment:
1. Create `netlify.toml` with similar configuration
2. Use Netlify Functions for Python endpoints
3. Configure build settings for React

## Testing

To test the application:

1. Get testnet USDC from faucets (if available)
2. Use testnet wallets with sufficient test ETH for gas
3. Test cross-chain transfers between different testnets
4. Verify attestation fetching works correctly
5. Test error handling (insufficient balance, wrong chain, etc.)

## Known Limitations

1. Message hash extraction may need refinement for all chains
2. Attestation polling timeout is fixed at 300 seconds
3. No automatic retry for failed attestation fetches
4. Frontend doesn't handle chain switching errors gracefully
5. No support for minting on destination chain (ready_to_mint status only)

## Future Enhancements

1. Add minting functionality on destination chain
2. Support for more chains (Optimism, zkSync, etc.)
3. Transaction history with filters and search
4. Email/SMS notifications for payment status
5. Admin dashboard for monitoring
6. API rate limiting and authentication
7. Webhook support for payment status updates

