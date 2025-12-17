# Cross-Chain USDC Payment Gateway

A full-stack application for cross-chain USDC transfers using Circle's Cross-Chain Transfer Protocol (CCTP). Built with Python Flask backend and React frontend, deployable as a single application on Vercel/Netlify.

## Features

- ✅ Multi-chain USDC transfers across 5+ testnets (Sepolia, Base Sepolia, Avalanche Fuji, Polygon Amoy, Arbitrum Sepolia)
- ✅ Real-time payment tracking with automatic status updates
- ✅ Wallet integration (MetaMask)
- ✅ Transaction history with detailed status timeline
- ✅ Background attestation fetching from Circle API
- ✅ Clean, modern UI with TailwindCSS
- ✅ Single-repo deployment ready for Vercel

## Architecture

- **Backend:** Python Flask with serverless functions
- **Frontend:** React 18 with Vite
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Blockchain:** Circle CCTP for cross-chain transfers

## Tech Stack

- **Backend:** Python 3.11, Flask, web3.py, requests
- **Frontend:** React 18, ethers.js, TailwindCSS
- **Database:** SQLite (local dev), PostgreSQL (production via environment)
- **Deployment:** Vercel serverless functions

## Project Structure

```
payment-gateway/
├── api/                          # Python serverless functions
│   ├── create_payment.py
│   ├── initiate_transfer.py
│   ├── check_status.py
│   └── utils/
│       ├── cctp_handler.py      # Core CCTP logic
│       ├── chain_config.py     # Chain configurations
│       └── db.py               # Database operations
├── src/                          # React frontend
│   ├── App.jsx
│   ├── components/
│   │   ├── PaymentForm.jsx
│   │   ├── TransactionTracker.jsx
│   │   └── ChainSelector.jsx
│   └── utils/
│       └── api.js              # Backend API calls
├── requirements.txt
├── package.json
└── vercel.json
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- MetaMask browser extension

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd payment-gateway
```

2. **Install frontend dependencies:**
```bash
npm install
```

3. **Install backend dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running Locally

1. **Start the backend (Flask dev server):**
```bash
# Option 1: Run unified server (recommended for local dev)
cd api
python server.py  # Runs all endpoints on port 5000

# Option 2: Run individual endpoints (for serverless testing)
cd api
python create_payment.py  # Runs on port 5000

# Option 3: Use Flask CLI
export FLASK_APP=server.py
flask run --port=5000
```

2. **Start the frontend (Vite dev server):**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to `http://localhost:5000`.

### Deployment to Netlify

1. **Install Netlify CLI (optional, for local testing):**
```bash
npm install -g netlify-cli
```

2. **Deploy via Netlify Dashboard:**
   - Connect your Git repository to Netlify
   - Set build command: `npm run build`
   - Set publish directory: `dist`
   - Netlify will automatically detect `netlify.toml` and configure functions

3. **Or deploy via CLI:**
```bash
netlify deploy --prod
```

The `netlify.toml` configuration handles:
- Python serverless functions in `netlify/functions/` directory
- Static build for React frontend
- Automatic redirects from `/api/*` to `/.netlify/functions/*`
- SPA routing fallback

**Note:** Both frontend and backend deploy to the same Netlify site. The API functions are accessible at `/.netlify/functions/<function-name>` and also via the `/api/*` redirects.

## Usage

1. **Connect Wallet:** Click "Connect Wallet" and approve MetaMask connection
2. **Create Payment:**
   - Enter USDC amount
   - Select source chain (where you're sending from)
   - Select destination chain (where recipient will receive)
   - Enter recipient address
   - Click "Initiate Payment"
3. **Approve Transactions:** MetaMask will prompt for:
   - USDC approval (to allow TokenMessenger to spend)
   - Burn transaction (depositForBurn)
4. **Track Status:** Switch to "Track Payments" tab to see real-time updates

## Payment Flow

1. **Create Payment:** Frontend creates payment record in database
2. **Approve & Burn:** User approves USDC spend and burns tokens on source chain
3. **Fetch Attestation:** Backend polls Circle API for attestation (proves burn)
4. **Mint (Future):** Once attestation is ready, USDC can be minted on destination chain

## API Endpoints

### `POST /api/create_payment`
Creates a new payment request.

**Request:**
```json
{
  "amount": 10.0,
  "source_chain": "sepolia",
  "dest_chain": "base_sepolia",
  "sender_address": "0x...",
  "recipient_address": "0x..."
}
```

**Response:**
```json
{
  "payment_id": "uuid",
  "status": "created"
}
```

### `POST /api/initiate_transfer`
Initiates transfer processing after burn transaction.

**Request:**
```json
{
  "payment_id": "uuid",
  "burn_tx_hash": "0x..."
}
```

### `GET /api/check_status/<payment_id>`
Get current payment status.

### `GET /api/recent_payments?limit=50`
Get recent payment history.

## Supported Chains

- **Ethereum Sepolia** (Domain: 0)
- **Base Sepolia** (Domain: 6)
- **Avalanche Fuji** (Domain: 1)
- **Polygon Amoy** (Domain: 7)
- **Arbitrum Sepolia** (Domain: 3)

## Development Notes

- The CCTP handler extracts message hashes from transaction logs
- Attestation polling happens in background threads to avoid blocking
- Database uses SQLite for development, can be swapped for PostgreSQL
- All chain configurations are centralized in `chain_config.py`

## Environment Variables

For local development, create a `.env` file:
```env
DATABASE_URL=payments.db          # SQLite path or PostgreSQL connection string
ALCHEMY_API_KEY=your_key_here     # Optional: for better RPC performance
```

For Netlify deployment, set environment variables in the Netlify dashboard:
- Go to Site settings → Environment variables
- Add `DATABASE_URL` (for production, use a PostgreSQL connection string)
- Add `ALCHEMY_API_KEY` if needed

**Note:** The frontend automatically detects if it's running in production and uses the correct API endpoints (Netlify functions vs local Flask server).

## License

MIT

