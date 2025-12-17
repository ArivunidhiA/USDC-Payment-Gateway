# Google OAuth Configuration Fix

## Issues Found in Your Google OAuth Setup:

Looking at your Google Cloud Console screenshot, I found **incorrect redirect URIs** that need to be fixed:

### ❌ **WRONG Redirect URIs (Remove these):**
1. `http://localhost:5173/auth/callback` - Should be `/api/auth/callback`
2. `https://your-site.netlify.app/auth/callback` - Should be `/api/auth/callback`
3. `https://your-site.netlify.app/.netlify/functions/auth_callt` - Truncated and wrong!

### ✅ **CORRECT Redirect URIs (Keep these):**
1. `http://localhost:5001/api/auth/callback` ✓
2. `https://your-site.netlify.app/api/auth/callback` ✓

### ✅ **CORRECT JavaScript Origins (These are fine):**
1. `http://localhost:5173` ✓
2. `https://your-site.netlify.app` ✓

## Steps to Fix:

1. **Go to Google Cloud Console** → APIs & Services → Credentials
2. **Click on your OAuth 2.0 Client ID**
3. **In "Authorized redirect URIs" section:**
   - **DELETE** these incorrect URIs:
     - `http://localhost:5173/auth/callback`
     - `https://your-site.netlify.app/auth/callback`
     - `https://your-site.netlify.app/.netlify/functions/auth_callt`
   - **KEEP** these correct URIs:
     - `http://localhost:5001/api/auth/callback`
     - `https://your-site.netlify.app/api/auth/callback`
4. **Click "SAVE"**

## Why This Matters:

The redirect URI must **exactly match** what your code sends to Google. Your code uses `/api/auth/callback`, so that's what must be in Google Console.

## After Fixing:

1. Wait 1-2 minutes for Google to update
2. Clear your browser cache/cookies
3. Try logging in again on Netlify

