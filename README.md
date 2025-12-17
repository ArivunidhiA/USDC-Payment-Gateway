# 💸 Cross-Chain USDC Payment Gateway

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![React](https://img.shields.io/badge/React-18.2-61dafb.svg)
![Netlify](https://img.shields.io/badge/Netlify-Deployed-00c7b7.svg)

> A production-ready full-stack application for seamless cross-chain USDC transfers using Circle's Cross-Chain Transfer Protocol (CCTP). Features OAuth2 authentication, PostgreSQL audit trails, and real-time transaction tracking across 5+ blockchain testnets.

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Supported Chains](#-supported-chains)
- [API Reference](#-api-reference)
- [License](#-license)

## 🎯 Overview

Cross-Chain USDC Payment Gateway enables secure, fast USDC transfers across multiple blockchain networks without bridges or wrapped tokens. Built with production-grade features including OAuth2 authentication, comprehensive audit trails, and real-time status tracking.

**Key Highlights:**
- ✅ **Zero Bridge Fees** - Direct USDC transfers via Circle CCTP
- ✅ **Multi-Chain Support** - 5+ testnet networks (Ethereum, Base, Avalanche, Polygon, Arbitrum)
- ✅ **Production Ready** - OAuth2, PostgreSQL, rate limiting, health checks
- ✅ **Real-Time Tracking** - Live transaction status updates with Circle attestation
- ✅ **Modern UI** - Smooth animations, dark theme, responsive design

## ✨ Features

### 🔐 Authentication & Security
- Google OAuth2 authentication with session management
- PostgreSQL-based audit trails for all user actions
- Rate limiting and security headers
- CSRF protection and secure session handling

### 💰 Payment Processing
- Multi-chain USDC transfers via Circle CCTP
- Real-time burn transaction tracking
- Automatic Circle attestation fetching
- Transaction history with detailed timelines

### 🎨 User Experience
- MetaMask wallet integration
- Interactive transaction tracking
- Demo mode for portfolio showcases
- Animated UI with Framer Motion
- Responsive design with TailwindCSS

### ⚡ Performance & Reliability
- Serverless architecture (Netlify Functions)
- Background attestation polling
- Health check endpoints
- Optimized for 100+ transactions/hour

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Login      │  │ Payment Form │  │   Tracker    │      │
│  │  (OAuth2)    │  │ (MetaMask)   │  │  (Real-time) │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTP/REST API
┌────────────────────────────┼─────────────────────────────┐
│                    Backend (Flask + Netlify)              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  API Endpoints (Serverless Functions)              │  │
│  │  • /api/auth/* (OAuth2)                            │  │
│  │  • /api/create_payment                             │  │
│  │  • /api/initiate_transfer                          │  │
│  │  • /api/check_status                               │  │
│  │  • /api/recent_payments                            │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌──────────────────┐         ┌──────────────────┐       │
│  │  CCTP Handler    │────────▶│ Circle API       │       │
│  │  (Burn/Mint)     │         │ (Attestation)    │       │
│  └──────────────────┘         └──────────────────┘       │
│  ┌──────────────────┐                                     │
│  │  PostgreSQL      │                                     │
│  │  • Payments      │                                     │
│  │  • Users         │                                     │
│  │  • Audit Logs    │                                     │
│  └──────────────────┘                                     │
└────────────────────────────────────────────────────────────┘
          │
          │ Web3 RPC
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Blockchain Networks (CCTP)                      │
│  Ethereum • Base • Avalanche • Polygon • Arbitrum          │
└─────────────────────────────────────────────────────────────┘
```

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 18 + Vite | User interface and wallet interactions |
| **Backend** | Flask + serverless-wsgi | API server and business logic |
| **Database** | PostgreSQL (SQLite dev) | Data persistence and audit trails |
| **Auth** | Google OAuth2 + Flask-Session | User authentication |
| **Blockchain** | web3.py + ethers.js | Smart contract interactions |
| **Deployment** | Netlify Functions | Serverless hosting |

## 🛠️ Tech Stack

### Backend
- **Python 3.11** - Core language
- **Flask 3.0** - Web framework
- **web3.py** - Blockchain interactions
- **SQLAlchemy** - ORM for database
- **authlib** - OAuth2 implementation
- **flask-limiter** - Rate limiting
- **psycopg2** - PostgreSQL adapter

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **ethers.js** - Ethereum library
- **Framer Motion** - Animations
- **TailwindCSS** - Styling
- **react-router-dom** - Routing

### Infrastructure
- **Netlify** - Hosting & serverless functions
- **PostgreSQL** - Production database
- **Circle CCTP** - Cross-chain protocol
- **MetaMask** - Wallet integration

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL (or use SQLite for dev)
- MetaMask browser extension

### Installation

```bash
# Clone repository
git clone https://github.com/ArivunidhiA/USDC-Payment-Gateway.git
cd USDC-Payment-Gateway

# Install frontend dependencies
npm install

# Install backend dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
# OAuth2
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Flask
FLASK_SECRET_KEY=generate-secure-random-key-here

# Circle CCTP (optional)
CIRCLE_API_KEY=your-circle-api-key

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### Run Locally

```bash
# Terminal 1: Start backend
cd api
python server.py  # Runs on port 5001

# Terminal 2: Start frontend
npm run dev  # Runs on port 5173
```

Visit `http://localhost:5173` and login with Google OAuth.

## 🔧 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth Client ID | `xxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth Client Secret | `xxx` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `FLASK_SECRET_KEY` | Yes | Flask session encryption key | Generate with `openssl rand -hex 32` |
| `FRONTEND_URL` | Yes | Frontend URL for OAuth redirects | `https://your-site.netlify.app` |
| `CIRCLE_API_KEY` | No | Circle API key (sandbox if not set) | `xxx` |

## 🚢 Deployment

### Deploy to Netlify

1. **Connect Repository** to Netlify dashboard
2. **Set Environment Variables** (see above)
3. **Build Settings** (auto-detected from `netlify.toml`):
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Python version: `3.11`
4. **Update Google OAuth** redirect URIs:
   - `https://your-site.netlify.app/.netlify/functions/auth_callback`
   - `https://your-site.netlify.app/api/auth/callback`
5. **Deploy** - Netlify automatically builds and deploys

See [NETLIFY_ENV_SETUP.md](./NETLIFY_ENV_SETUP.md) for detailed configuration.

## 🌐 Supported Chains

| Chain | Domain | Testnet |
|-------|--------|---------|
| Ethereum | 0 | Sepolia |
| Avalanche | 1 | Fuji |
| Arbitrum | 3 | Sepolia |
| Base | 6 | Sepolia |
| Polygon | 7 | Amoy |

All chains use Circle CCTP for native USDC transfers.

## 📡 API Reference

### `POST /api/create_payment`
Create a new payment request.

```json
{
  "amount": 10.0,
  "source_chain": "sepolia",
  "dest_chain": "base_sepolia",
  "sender_address": "0x...",
  "recipient_address": "0x..."
}
```

### `POST /api/initiate_transfer`
Initiate transfer after burn transaction.

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Circle CCTP**
