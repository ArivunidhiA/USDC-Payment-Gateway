# Netlify Deployment Guide

This project is configured to deploy both frontend and backend to a single Netlify site.

## Architecture

- **Frontend**: React app built with Vite, served as static files
- **Backend**: Python Flask functions deployed as Netlify serverless functions
- **Database**: SQLite for development, PostgreSQL recommended for production

## Project Structure

```
.
├── netlify/
│   └── functions/          # Netlify serverless functions
│       ├── create_payment.py
│       ├── initiate_transfer.py
│       ├── check_status.py
│       ├── recent_payments.py
│       └── requirements.txt
├── api/                     # Shared utilities (imported by functions)
│   └── utils/
│       ├── chain_config.py
│       ├── cctp_handler.py
│       └── db.py
├── src/                     # React frontend
├── netlify.toml            # Netlify configuration
└── dist/                   # Build output (generated)
```

## How It Works

1. **Build Process**:
   - Netlify runs `npm run build` which builds the React app to `dist/`
   - Python functions in `netlify/functions/` are automatically detected
   - Netlify installs Python dependencies from `netlify/functions/requirements.txt`

2. **Routing**:
   - Frontend routes (`/`, `/create`, etc.) serve the React app
   - API routes (`/api/*`) are redirected to `/.netlify/functions/*`
   - The `netlify.toml` file handles all redirects

3. **API Endpoints**:
   - `/api/create_payment` → `/.netlify/functions/create_payment`
   - `/api/initiate_transfer` → `/.netlify/functions/initiate_transfer`
   - `/api/check_status/:id` → `/.netlify/functions/check_status/:id`
   - `/api/recent_payments` → `/.netlify/functions/recent_payments`

## Deployment Steps

### Option 1: Netlify Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [Netlify Dashboard](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your Git repository

2. **Configure Build Settings** (usually auto-detected):
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Python version: `3.11` (set in `netlify.toml`)

3. **Set Environment Variables**:
   - Go to Site settings → Environment variables
   - Add:
     - `DATABASE_URL`: PostgreSQL connection string (for production)
     - `ALCHEMY_API_KEY`: (optional) For better RPC performance

4. **Deploy**:
   - Click "Deploy site"
   - Netlify will automatically build and deploy

### Option 2: Netlify CLI

1. **Install CLI**:
   ```bash
   npm install -g netlify-cli
   ```

2. **Login**:
   ```bash
   netlify login
   ```

3. **Initialize** (first time only):
   ```bash
   netlify init
   ```

4. **Deploy**:
   ```bash
   netlify deploy --prod
   ```

## Local Development with Netlify

Test the Netlify setup locally:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Run Netlify dev server (simulates production)
netlify dev
```

This will:
- Start the React dev server
- Run Netlify functions locally
- Simulate the production environment

## Environment Variables

### Development
Create a `.env` file in the root:
```env
DATABASE_URL=payments.db
ALCHEMY_API_KEY=your_key_here
```

### Production (Netlify)
Set in Netlify Dashboard → Site settings → Environment variables:
- `DATABASE_URL`: Use a PostgreSQL connection string (e.g., from Supabase, Railway, etc.)
- `ALCHEMY_API_KEY`: Your Alchemy API key (optional)

## Database Setup for Production

For production, use PostgreSQL instead of SQLite:

1. **Create PostgreSQL Database**:
   - Use services like Supabase, Railway, or Neon
   - Get the connection string

2. **Update Environment Variable**:
   - Set `DATABASE_URL` in Netlify to your PostgreSQL connection string
   - Format: `postgresql://user:password@host:port/database`

3. **Update `api/utils/db.py`** (if needed):
   - The current implementation uses SQLite
   - For PostgreSQL, you may need to install `psycopg2`:
     ```bash
     pip install psycopg2-binary
     ```
   - Add to `netlify/functions/requirements.txt`

## Troubleshooting

### Functions Not Working

1. **Check Function Logs**:
   - Go to Netlify Dashboard → Functions → View logs
   - Look for import errors or runtime errors

2. **Verify Python Version**:
   - Ensure `netlify.toml` specifies `PYTHON_VERSION = "3.11"`

3. **Check Dependencies**:
   - Verify `netlify/functions/requirements.txt` has all packages
   - Netlify installs these automatically

### API Routes Not Found

1. **Check Redirects**:
   - Verify `netlify.toml` has correct redirect rules
   - Test redirects in Netlify Dashboard → Redirects

2. **Verify Function Names**:
   - Function file names must match redirect paths
   - `create_payment.py` → `/.netlify/functions/create_payment`

### Build Failures

1. **Check Build Logs**:
   - View detailed logs in Netlify Dashboard
   - Look for npm or Python errors

2. **Verify Node/Python Versions**:
   - Check `netlify.toml` for correct versions
   - Ensure versions are supported by Netlify

## Testing Production Locally

Use Netlify CLI to simulate production:

```bash
# Build the project
npm run build

# Start Netlify dev (uses production build)
netlify dev
```

This runs:
- Built React app (from `dist/`)
- Netlify functions (from `netlify/functions/`)
- Same routing as production

## Important Notes

1. **Single Deployment**: Both frontend and backend deploy to the same Netlify site
2. **Function Cold Starts**: First request to a function may be slower (cold start)
3. **Database**: SQLite files are ephemeral in serverless - use PostgreSQL for production
4. **File System**: Serverless functions have read-only filesystem except `/tmp`
5. **Timeouts**: Netlify functions have execution time limits (10s for free tier, 26s for pro)

## Cost Considerations

- **Free Tier**: 125K function invocations/month
- **Pro Tier**: 1M function invocations/month
- **Bandwidth**: 100GB/month (free), 1TB/month (pro)

For high-traffic applications, consider:
- Caching API responses
- Using Netlify Edge Functions (faster, cheaper)
- Optimizing function execution time

