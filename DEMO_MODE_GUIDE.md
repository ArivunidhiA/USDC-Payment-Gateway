# 🎭 Demo Mode Guide

## Overview

Demo Mode allows visitors to see the application working with sample transactions **without** requiring:
- MetaMask wallet connection
- Testnet tokens
- Making actual blockchain transactions

## ✅ What Was Implemented

### 1. Database Seeding
- **File**: `api/seed_demo_data.py`
- **Demo User**: `demo@usdcgateway.com`
- **Sample Transactions**: 8 transactions with various statuses

### 2. Demo Mode Toggle
- **Location**: Header button (🎭 Demo Mode)
- **State**: Green when active, gray when off
- **Functionality**: Switches between demo and real data

### 3. Sample Transaction Statuses
- ✅ **Completed** (3 transactions) - Successful cross-chain transfers
- ⏳ **Pending** (1 transaction) - Just created
- 🔥 **Burning** (1 transaction) - USDC being burned on source chain
- 🔍 **Fetching Attestation** (1 transaction) - Waiting for Circle confirmation
- ✅ **Ready to Mint** (1 transaction) - Attestation received, ready for minting
- ❌ **Failed** (1 transaction) - Transaction that failed

## 🚀 How to Use

### For Visitors/Portfolio Demo

1. **Start the Application**
   ```bash
   # Terminal 1 - Backend
   cd api
   python server.py
   
   # Terminal 2 - Frontend
   npm run dev
   ```

2. **Login** (Google OAuth required)

3. **Enable Demo Mode**
   - Click the **"🎭 Demo Mode"** button in the header
   - Button turns green (🎭 Demo Mode ON)

4. **View Sample Transactions**
   - Go to "Track Payments" tab
   - See 8 sample transactions with various statuses
   - Click any transaction to see details
   - View transaction timelines, status updates, etc.

5. **Try Creating Payment** (Optional)
   - In demo mode, wallet connection is not required
   - Form shows demo banner explaining the mode
   - Toggle off demo mode to create real payments

### For Real Usage

1. **Disable Demo Mode**
   - Click "🎭 Demo Mode ON" to toggle it off

2. **Connect Wallet**
   - Click "Connect Wallet" button
   - Approve MetaMask connection

3. **Create Real Payment**
   - Fill out payment form
   - Approve and execute transactions
   - View your real transactions

## 📊 Sample Data Details

The demo includes realistic transaction data:

| Amount | Source → Destination | Status | Details |
|--------|---------------------|--------|---------|
| $150.00 | Sepolia → Base Sepolia | ✅ Completed | Full transfer with both burn and mint tx hashes |
| $75.50 | Avalanche → Polygon | 🔍 Fetching Attestation | Burn complete, waiting for Circle |
| $250.00 | Arbitrum → Sepolia | ✅ Ready to Mint | Attestation received |
| $50.25 | Polygon → Base | 🔥 Burning | USDC burn in progress |
| $500.00 | Base → Avalanche | ✅ Completed | Large successful transfer |
| $25.75 | Sepolia → Arbitrum | ❌ Failed | Transaction that failed |
| $1,000.00 | Avalanche → Sepolia | ✅ Completed | High-value successful transfer |
| $33.33 | Polygon → Arbitrum | ⏳ Pending | Just created, no transactions yet |

## 🔧 Technical Implementation

### Backend Changes

**API Endpoint** (`api/server.py`):
```python
@app.route('/api/recent_payments', methods=['GET'])
def recent_payments():
    demo_mode = request.args.get('demo', 'false').lower() == 'true'
    if demo_mode:
        # Return demo user's payments
    else:
        # Return current user's payments
```

### Frontend Changes

**App Component** (`src/App.jsx`):
- Added `demoMode` state
- Demo mode toggle button in header
- Passes `demoMode` to payment loading

**Payment Form** (`src/components/PaymentForm.jsx`):
- Shows demo banner when active
- Hides wallet connection requirement
- Disables form submission in demo mode

**API Client** (`src/utils/api.js`):
- `fetchRecentPayments()` accepts `demoMode` parameter
- Passes to backend API

## 🎯 Benefits

1. **Instant Demo**: Visitors see working transactions immediately
2. **No Setup Required**: No MetaMask, no tokens, no configuration
3. **Professional Presentation**: Shows real functionality with realistic data
4. **Flexible**: Real mode still works for actual transactions
5. **Portfolio Ready**: Perfect for showcasing on resume/portfolio

## 📝 Notes

- Demo transactions use realistic transaction hashes and addresses
- All demo data is stored in the database (same as real data)
- Demo mode can be toggled on/off anytime
- Demo user's transactions are separate from real user transactions
- To reset demo data, run `python seed_demo_data.py` again

## 🔄 Resetting Demo Data

To regenerate demo transactions:

```bash
cd api
python seed_demo_data.py
```

This will:
- Create/update demo user
- Create 8 new sample transactions
- Preserve existing real user data

