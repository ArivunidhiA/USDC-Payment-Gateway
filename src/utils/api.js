/**
 * API client for backend communication.
 * All backend endpoints return JSON.
 * 
 * For Netlify: Uses /.netlify/functions/ prefix
 * For local dev: Uses /api prefix (proxied by Vite)
 */

// Determine if we're in production (Netlify) or development
const isProduction = import.meta.env.PROD;
const API_BASE = import.meta.env.VITE_API_URL || '';

// Netlify functions use /.netlify/functions/ prefix
// In production, we use the Netlify function URLs via redirects
// In development, we use /api which is proxied to local Flask server
const getApiUrl = (endpoint) => {
  if (API_BASE) {
    return `${API_BASE}${endpoint}`;
  }
  // In production, Netlify redirects /api/* to /.netlify/functions/*
  // So we can just use /api/* and Netlify will handle the redirect
  // In development, /api is proxied to local Flask server
  return endpoint;
};

async function fetchAPI(endpoint, options = {}) {
  const url = getApiUrl(endpoint);
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Include cookies for session
    ...options,
  });

  if (!response.ok) {
    // Handle 401 (unauthorized) - redirect to login
    if (response.status === 401) {
      // Don't throw, let the component handle it
      const error = await response.json().catch(() => ({ error: 'Unauthorized' }));
      throw new Error(error.error || 'Authentication required');
    }
    const error = await response.json();
    throw new Error(error.error || 'API request failed');
  }

  return response.json();
}

export async function createPayment(data) {
  return fetchAPI('/api/create_payment', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function initiateBurn(data) {
  return fetchAPI('/api/initiate_transfer', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function checkPaymentStatus(paymentId) {
  return fetchAPI(`/api/check_status/${paymentId}`);
}

export async function fetchRecentPayments(limit = 50, demoMode = false) {
  const data = await fetchAPI(`/api/recent_payments?limit=${limit}&demo=${demoMode}`, {
    credentials: 'include', // Include cookies for session
  });
  return data.payments;
}

export async function getCurrentUser() {
  return fetchAPI('/api/auth/user', {
    credentials: 'include',
  });
}

export async function logout() {
  return fetchAPI('/api/auth/logout', {
    method: 'POST',
    credentials: 'include',
  });
}

