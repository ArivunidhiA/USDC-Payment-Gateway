# 🔧 OAuth Redirect URI Fix

## ✅ Fixed!

The OAuth redirect URI has been corrected. You need to add the exact redirect URI to Google Cloud Console.

## 📝 Steps to Fix OAuth

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/apis/credentials

### 2. Select Your OAuth 2.0 Client
- Find your OAuth client (the one with Client ID: `38118865020-60rjic2tsa0284tegf53c67ed8tsjf5q`)
- Click on it to edit

### 3. Add Authorized Redirect URI
In the "Authorized redirect URIs" section, click **"+ ADD URI"** and add:

```
http://localhost:5001/api/auth/callback
```

**Important:** 
- Must be **exactly** this URL (no trailing slash, no query parameters)
- Make sure there are no extra spaces
- Click **"SAVE"** after adding

### 4. Test Again
1. Go to http://localhost:5173
2. Click "Continue with Google"
3. It should work now! ✅

## 🔍 What Was Fixed

The redirect URI was including query parameters which caused a mismatch. Now it uses:
- **Exact URI**: `http://localhost:5001/api/auth/callback`
- Query parameters are handled via session storage instead

## 📋 For Production (Later)

When you deploy to Netlify, you'll need to add:
```
https://your-site.netlify.app/api/auth/callback
```

But for now, just add the localhost one above.

