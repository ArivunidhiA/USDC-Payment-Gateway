"""
Load testing configuration for USDC Payment Gateway.

Tests:
- 100+ transactions per hour
- Concurrent user load
- API endpoint performance
- Database query performance
"""

from locust import HttpUser, task, between
import random
import json

# Test data
CHAINS = ['sepolia', 'base_sepolia', 'avalanche_fuji', 'polygon_amoy', 'arbitrum_sepolia']


class PaymentGatewayUser(HttpUser):
    """Simulates a user interacting with the payment gateway."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts. Simulate login."""
        # In real scenario, would authenticate here
        # For load testing, we'll use mock authentication
        self.user_id = f"test_user_{random.randint(1000, 9999)}"
        self.payment_ids = []
    
    @task(3)
    def check_health(self):
        """Check health endpoint - most frequent operation."""
        self.client.get("/api/health")
    
    @task(2)
    def get_recent_payments(self):
        """Get recent payments - common operation."""
        self.client.get(
            "/api/recent_payments",
            headers={"Authorization": f"Bearer mock_token_{self.user_id}"}
        )
    
    @task(1)
    def create_payment(self):
        """Create a payment - less frequent but important."""
        source_chain = random.choice(CHAINS)
        dest_chain = random.choice([c for c in CHAINS if c != source_chain])
        
        payload = {
            "amount": round(random.uniform(1.0, 100.0), 2),
            "source_chain": source_chain,
            "dest_chain": dest_chain,
            "sender_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            "recipient_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
        }
        
        response = self.client.post(
            "/api/create_payment",
            json=payload,
            headers={"Authorization": f"Bearer mock_token_{self.user_id}"}
        )
        
        if response.status_code == 201:
            data = response.json()
            if 'payment_id' in data:
                self.payment_ids.append(data['payment_id'])
    
    @task(1)
    def check_payment_status(self):
        """Check status of a payment."""
        if self.payment_ids:
            payment_id = random.choice(self.payment_ids)
            self.client.get(
                f"/api/check_status/{payment_id}",
                headers={"Authorization": f"Bearer mock_token_{self.user_id}"}
            )
    
    @task(1)
    def get_audit_logs(self):
        """Get audit logs."""
        self.client.get(
            "/api/audit_logs",
            headers={"Authorization": f"Bearer mock_token_{self.user_id}"}
        )


class HighLoadUser(HttpUser):
    """Simulates high-load scenario - 100+ transactions/hour."""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task(10)
    def rapid_health_checks(self):
        """Rapid health checks for monitoring."""
        self.client.get("/api/health")
    
    @task(5)
    def rapid_payment_creation(self):
        """Rapid payment creation for load testing."""
        source_chain = random.choice(CHAINS)
        dest_chain = random.choice([c for c in CHAINS if c != source_chain])
        
        payload = {
            "amount": round(random.uniform(0.1, 10.0), 2),
            "source_chain": source_chain,
            "dest_chain": dest_chain,
            "sender_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            "recipient_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
        }
        
        self.client.post(
            "/api/create_payment",
            json=payload,
            headers={"Authorization": "Bearer mock_token"}
        )

