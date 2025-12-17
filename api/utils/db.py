"""
Database operations with PostgreSQL support and audit trails.

Uses SQLAlchemy for database abstraction. Falls back to SQLite if PostgreSQL unavailable.
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Text, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    picture = Column(String)
    oauth_provider = Column(String)
    oauth_id = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Payment(Base):
    __tablename__ = 'payments'
    
    payment_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False, index=True)
    amount_usd = Column(Float, nullable=False)
    source_chain = Column(String, nullable=False)
    dest_chain = Column(String, nullable=False)
    sender_address = Column(String, nullable=False)
    recipient_address = Column(String, nullable=False)
    burn_tx_hash = Column(String)
    mint_tx_hash = Column(String)
    status = Column(String, default='pending', index=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    payment_metadata = Column(Text)  # JSON string of payment metadata (renamed from 'metadata' - reserved in SQLAlchemy)
    
    # Relationship
    user = relationship("User", backref="payments")


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), index=True)
    action = Column(String, nullable=False, index=True)  # 'create_payment', 'update_payment', 'login', etc.
    resource_type = Column(String)  # 'payment', 'user', etc.
    resource_id = Column(String, index=True)  # payment_id, user_id, etc.
    details = Column(Text)  # JSON string with additional details
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=func.now(), index=True)


# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///payments.db')

# Handle PostgreSQL connection string format
if DATABASE_URL.startswith('postgresql://'):
    # SQLAlchemy uses 'postgresql://' but some providers give 'postgres://'
    if 'postgres://' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    # Add connection pooling for PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        echo=False
    )
else:
    # SQLite fallback
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, caller should close


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


# User operations
def create_user(email, name=None, picture=None, oauth_provider=None, oauth_id=None):
    """Create a new user."""
    import uuid
    db = SessionLocal()
    try:
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            email=email,
            name=name,
            picture=picture,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Audit log
        log_audit(
            user_id=user_id,
            action='user_created',
            resource_type='user',
            resource_id=user_id,
            details=json.dumps({'email': email, 'oauth_provider': oauth_provider})
        )
        
        return user_id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_user_by_email(email):
    """Get user by email."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        } if user else None
    finally:
        db.close()


def get_user_by_id(user_id):
    """Get user by ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        return {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        } if user else None
    finally:
        db.close()


# Payment operations
def create_payment(payment_id, amount, source_chain, dest_chain, sender, recipient, user_id=None):
    """Insert new payment record with audit trail."""
    db = SessionLocal()
    try:
        payment = Payment(
            payment_id=payment_id,
            user_id=user_id or 'anonymous',
            amount_usd=float(amount),
            source_chain=source_chain,
            dest_chain=dest_chain,
            sender_address=sender,
            recipient_address=recipient,
            status='pending'
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Audit log
        log_audit(
            user_id=user_id,
            action='create_payment',
            resource_type='payment',
            resource_id=payment_id,
            details=json.dumps({
                'amount': amount,
                'source_chain': source_chain,
                'dest_chain': dest_chain
            })
        )
        
        return payment_id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def update_payment(payment_id, user_id=None, **kwargs):
    """Update payment fields dynamically with audit trail."""
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            return False
        
        # Track changes
        changes = {}
        for key, value in kwargs.items():
            if hasattr(payment, key):
                old_value = getattr(payment, key)
                setattr(payment, key, value)
                changes[key] = {'old': str(old_value), 'new': str(value)}
        
        payment.updated_at = datetime.utcnow()
        db.commit()
        
        # Audit log
        log_audit(
            user_id=user_id or payment.user_id,
            action='update_payment',
            resource_type='payment',
            resource_id=payment_id,
            details=json.dumps(changes)
        )
        
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_payment(payment_id):
    """Fetch payment by ID."""
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if payment:
            return {
                'payment_id': payment.payment_id,
                'user_id': payment.user_id,
                'amount_usd': payment.amount_usd,
                'source_chain': payment.source_chain,
                'dest_chain': payment.dest_chain,
                'sender_address': payment.sender_address,
                'recipient_address': payment.recipient_address,
                'burn_tx_hash': payment.burn_tx_hash,
                'mint_tx_hash': payment.mint_tx_hash,
                'status': payment.status,
                'created_at': payment.created_at.isoformat() if payment.created_at else None,
                'updated_at': payment.updated_at.isoformat() if payment.updated_at else None,
                'metadata': payment.payment_metadata
            }
        return None
    finally:
        db.close()


def get_recent_payments(limit=50, user_id=None):
    """Get most recent payments, optionally filtered by user."""
    db = SessionLocal()
    try:
        query = db.query(Payment)
        if user_id:
            query = query.filter(Payment.user_id == user_id)
        payments = query.order_by(Payment.created_at.desc()).limit(limit).all()
        
        return [{
            'payment_id': p.payment_id,
            'user_id': p.user_id,
            'amount_usd': p.amount_usd,
            'source_chain': p.source_chain,
            'dest_chain': p.dest_chain,
            'sender_address': p.sender_address,
            'recipient_address': p.recipient_address,
            'burn_tx_hash': p.burn_tx_hash,
            'mint_tx_hash': p.mint_tx_hash,
            'status': p.status,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
            'metadata': p.payment_metadata
        } for p in payments]
    finally:
        db.close()


# Audit trail operations
def log_audit(user_id=None, action=None, resource_type=None, resource_id=None, 
              details=None, ip_address=None, user_agent=None):
    """Create an audit log entry."""
    db = SessionLocal()
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        db.rollback()
        # Don't fail if audit logging fails
        print(f"Audit logging failed: {e}")
    finally:
        db.close()


def get_audit_logs(limit=100, user_id=None, action=None, resource_type=None):
    """Get audit logs with filters."""
    db = SessionLocal()
    try:
        query = db.query(AuditLog)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        return [{
            'log_id': log.log_id,
            'user_id': log.user_id,
            'action': log.action,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'details': log.details,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'created_at': log.created_at.isoformat() if log.created_at else None
        } for log in logs]
    finally:
        db.close()


# Initialize DB on import
init_db()
