# 🚨 URGENT: Google OAuth Redirect URI Fix

## ❌ WRONG Redirect URIs (DELETE THESE NOW):

From your screenshot, you have **TWO INCORRECT** redirect URIs that MUST be removed:

1. ❌ `http://localhost:5173/auth/callback` - **DELETE THIS**
2. ❌ `https://usdc-payment-gateway.netlify.app/auth/callback` - **DELETE THIS**

## ✅ CORRECT Redirect URIs (KEEP THESE):

1. ✅ `http://localhost:5001/api/auth/callback` - **KEEP**
2. ✅ `https://usdc-payment-gateway.netlify.app/api/auth/callback` - **KEEP**

## 📋 Steps to Fix:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Scroll to "Authorized redirect URIs"
4. **DELETE** the two wrong ones listed above
5. **KEEP** only the two correct ones
6. Click **"SAVE"**
7. Wait 1-2 minutes for changes to propagate

## ⚠️ Why This Matters:

Google OAuth requires **EXACT** match of redirect URIs. If you have wrong URIs, the OAuth flow will fail even if the code is correct.

