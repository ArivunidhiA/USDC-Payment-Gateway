"""
Seed database with demo transactions for showcasing the project.
Run this once to populate the database with sample data.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
import uuid
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.db import SessionLocal, User, Payment, init_db, create_user, create_payment, update_payment

load_dotenv()

def seed_demo_data():
    """Create demo user and sample transactions."""
    db = SessionLocal()
    
    try:
        # Initialize database tables
        init_db()
        
        # Create demo user (or use existing)
        demo_email = "demo@usdcgateway.com"
        demo_user = db.query(User).filter(User.email == demo_email).first()
        
        if not demo_user:
            user_id = create_user(
                email=demo_email,
                name="Demo User",
                picture="https://ui-avatars.com/api/?name=Demo+User&background=6366f1&color=fff",
                oauth_provider="demo",
                oauth_id="demo_user_123"
            )
            print(f"✅ Created demo user: {user_id}")
        else:
            user_id = demo_user.user_id
            print(f"✅ Using existing demo user: {user_id}")
        
        # Sample transactions with various statuses
        sample_transactions = [
            {
                "amount": 150.00,
                "source_chain": "sepolia",
                "dest_chain": "base_sepolia",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "completed",
                "burn_tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "mint_tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "days_ago": 2
            },
            {
                "amount": 75.50,
                "source_chain": "avalanche_fuji",
                "dest_chain": "polygon_amoy",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "fetching_attestation",
                "burn_tx_hash": "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba",
                "mint_tx_hash": None,
                "days_ago": 0.5
            },
            {
                "amount": 250.00,
                "source_chain": "arbitrum_sepolia",
                "dest_chain": "sepolia",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "ready_to_mint",
                "burn_tx_hash": "0x5555555555555555555555555555555555555555555555555555555555555555",
                "mint_tx_hash": None,
                "days_ago": 1
            },
            {
                "amount": 50.25,
                "source_chain": "polygon_amoy",
                "dest_chain": "base_sepolia",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "burning",
                "burn_tx_hash": "0x1111111111111111111111111111111111111111111111111111111111111111",
                "mint_tx_hash": None,
                "days_ago": 0.1
            },
            {
                "amount": 500.00,
                "source_chain": "base_sepolia",
                "dest_chain": "avalanche_fuji",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "completed",
                "burn_tx_hash": "0x2222222222222222222222222222222222222222222222222222222222222222",
                "mint_tx_hash": "0x3333333333333333333333333333333333333333333333333333333333333333",
                "days_ago": 5
            },
            {
                "amount": 25.75,
                "source_chain": "sepolia",
                "dest_chain": "arbitrum_sepolia",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "failed",
                "burn_tx_hash": "0x4444444444444444444444444444444444444444444444444444444444444444",
                "mint_tx_hash": None,
                "days_ago": 3
            },
            {
                "amount": 1000.00,
                "source_chain": "avalanche_fuji",
                "dest_chain": "sepolia",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "completed",
                "burn_tx_hash": "0x6666666666666666666666666666666666666666666666666666666666666666",
                "mint_tx_hash": "0x7777777777777777777777777777777777777777777777777777777777777777",
                "days_ago": 7
            },
            {
                "amount": 33.33,
                "source_chain": "polygon_amoy",
                "dest_chain": "arbitrum_sepolia",
                "sender": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "recipient": "0x8ba1f109551bD432803012645Hac136c22C1779",
                "status": "pending",
                "burn_tx_hash": None,
                "mint_tx_hash": None,
                "days_ago": 0.05
            }
        ]
        
        # Create sample payments
        created_count = 0
        for tx in sample_transactions:
            payment_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc) - timedelta(days=tx["days_ago"])
            
            # Create payment
            create_payment(
                payment_id=payment_id,
                amount=tx["amount"],
                source_chain=tx["source_chain"],
                dest_chain=tx["dest_chain"],
                sender=tx["sender"],
                recipient=tx["recipient"],
                user_id=user_id
            )
            
            # Update with status and transaction hashes
            update_data = {
                "status": tx["status"],
            }
            
            if tx["burn_tx_hash"]:
                update_data["burn_tx_hash"] = tx["burn_tx_hash"]
            if tx["mint_tx_hash"]:
                update_data["mint_tx_hash"] = tx["mint_tx_hash"]
            
            # Update payment with all fields including timestamps
            db_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
            if db_payment:
                db_payment.status = tx["status"]
                db_payment.created_at = created_at
                db_payment.updated_at = created_at + timedelta(hours=1) if tx["status"] != "pending" else created_at
                if tx["burn_tx_hash"]:
                    db_payment.burn_tx_hash = tx["burn_tx_hash"]
                if tx["mint_tx_hash"]:
                    db_payment.mint_tx_hash = tx["mint_tx_hash"]
                db.commit()
            
            created_count += 1
        
        print(f"✅ Created {created_count} demo transactions")
        print(f"\n📊 Demo Data Summary:")
        print(f"   - User: {demo_email}")
        print(f"   - Transactions: {created_count}")
        print(f"   - Statuses: completed, pending, burning, fetching_attestation, ready_to_mint, failed")
        print(f"\n🎉 Demo data seeded successfully!")
        print(f"\n💡 To use demo mode:")
        print(f"   1. Login with Google OAuth")
        print(f"   2. Toggle 'Demo Mode' in the UI")
        print(f"   3. View sample transactions without connecting wallet")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()

