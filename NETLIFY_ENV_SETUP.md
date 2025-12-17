# Netlify Environment Variables Setup

When deploying to Netlify, you need to configure environment variables in the Netlify dashboard. Follow these steps:

## Required Environment Variables

### 1. Flask Secret Key
- **Variable:** `FLASK_SECRET_KEY`
- **Value:** Generate a secure random string (e.g., use `openssl rand -hex 32`)
- **Purpose:** Used for session encryption and CSRF protection

### 2. Database URL (PostgreSQL)
- **Variable:** `DATABASE_URL`
- **Value:** Your PostgreSQL connection string
- **Format:** `postgresql://username:password@host:port/database`
- **Purpose:** Database connection for payments, users, and audit logs
- **Note:** You can use Supabase, Neon, or any PostgreSQL provider

### 3. Google OAuth Credentials
- **Variable:** `GOOGLE_CLIENT_ID`
- **Value:** Your Google OAuth Client ID (from Google Cloud Console)
- **Format:** `xxxxx.apps.googleusercontent.com`

- **Variable:** `GOOGLE_CLIENT_SECRET`
- **Value:** Your Google OAuth Client Secret

- **Purpose:** User authentication via Google Sign-In

### 4. Circle API Key (Optional)
- **Variable:** `CIRCLE_API_KEY`
- **Value:** Your Circle API key from Circle Console
- **Purpose:** Access to Circle's CCTP attestation API
- **Note:** If not provided, the app will use the sandbox API

### 5. Frontend URL
- **Variable:** `FRONTEND_URL`
- **Value:** Your Netlify site URL (e.g., `https://your-site.netlify.app`)
- **Purpose:** OAuth redirect URL configuration

## How to Set Environment Variables in Netlify

1. Go to your Netlify dashboard
2. Select your site
3. Navigate to **Site settings** → **Environment variables**
4. Click **Add a variable**
5. Add each variable with its value
6. Click **Save**

## Important Security Notes

- ✅ **Never commit** `.env` files to Git
- ✅ **Never commit** API keys or secrets to the repository
- ✅ All environment variables are automatically injected into Netlify Functions
- ✅ Use Netlify's encrypted environment variables for production
- ✅ Keep your `FLASK_SECRET_KEY` and `GOOGLE_CLIENT_SECRET` secure

## Verifying Environment Variables

After deployment, you can verify environment variables are loaded:

1. Check the function logs in Netlify dashboard
2. The `/api/health` endpoint should return success
3. Try logging in with Google OAuth to verify credentials

## Troubleshooting

- **"Authentication required" errors:** Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- **Database connection errors:** Verify `DATABASE_URL` format and credentials
- **OAuth redirect errors:** Ensure `FRONTEND_URL` matches your Netlify site URL and is added to Google OAuth authorized redirect URIs

