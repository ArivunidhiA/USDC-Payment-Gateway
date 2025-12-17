# Load Testing for USDC Payment Gateway

This directory contains load testing configuration using Locust.

## Setup

1. Install Locust:
```bash
pip install -r requirements.txt
```

## Running Load Tests

### Basic Load Test
```bash
locust -f locustfile.py --host=http://localhost:5001
```

Then open http://localhost:8089 in your browser to start the test.

### Command Line Load Test (100+ transactions/hour)
```bash
locust -f locustfile.py \
  --host=http://localhost:5001 \
  --users=50 \
  --spawn-rate=10 \
  --run-time=1h \
  --headless \
  --html=report.html
```

### High Load Test
```bash
locust -f locustfile.py \
  --host=http://localhost:5001 \
  --users=100 \
  --spawn-rate=20 \
  --run-time=30m \
  --headless \
  --html=high_load_report.html
```

## Test Scenarios

1. **Normal Load**: 10-20 concurrent users
2. **High Load**: 50-100 concurrent users (100+ tx/hour)
3. **Stress Test**: 100+ concurrent users

## Metrics to Monitor

- Requests per second (RPS)
- Response times (p50, p95, p99)
- Error rate
- Database query performance
- Memory and CPU usage

## Expected Results

- **100+ transactions/hour**: Achieved with 50+ concurrent users
- **Response time**: < 500ms for 95% of requests
- **Error rate**: < 1%
- **Uptime**: 99.9% availability

## Reports

Reports are generated as HTML files. Open them in a browser to view detailed metrics.

