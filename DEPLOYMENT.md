# Deployment Guide

## 🚀 Deployment Options

### Option 1: Render.com (Recommended)

Render provides free tier hosting perfect for this backend.

#### Steps:

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `backend-kiro1` directory

3. **Configure Service**
   ```
   Name: memory-layer-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   Go to "Environment" tab and add:
   ```
   OPENAI_API_KEY=sk-...
   SUPABASE_URL=https://...
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   SUPABASE_JWT_SECRET=...
   ADMIN_API_KEY=...
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - Your API will be at `https://your-service.onrender.com`

#### Free Tier Limitations:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free

### Option 2: Railway.app

Similar to Render with generous free tier.

#### Steps:

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure**
   ```
   Root Directory: backend-kiro1
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Variables**
   Same as Render (see above)

5. **Deploy**
   - Railway auto-deploys on push
   - Get URL from dashboard

### Option 3: Fly.io

Great for global deployment with edge locations.

#### Steps:

1. **Install Fly CLI**
   ```bash
   # macOS
   brew install flyctl
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   flyctl auth login
   ```

3. **Create fly.toml**
   ```toml
   app = "memory-layer-backend"
   
   [build]
     builder = "paketobuildpacks/builder:base"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

4. **Deploy**
   ```bash
   cd backend-kiro1
   flyctl launch
   flyctl secrets set OPENAI_API_KEY=sk-...
   flyctl secrets set SUPABASE_URL=https://...
   # ... add all secrets
   flyctl deploy
   ```

### Option 4: Docker (Self-Hosted)

Deploy anywhere that supports Docker.

#### Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run:

```bash
# Build image
docker build -t memory-layer-backend .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e SUPABASE_URL=https://... \
  -e SUPABASE_SERVICE_ROLE_KEY=eyJ... \
  -e SUPABASE_JWT_SECRET=... \
  -e ADMIN_API_KEY=... \
  memory-layer-backend
```

#### Docker Compose:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## 🔧 Post-Deployment Configuration

### 1. Update CORS Origins

In `main.py`, update allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "https://your-domain.com"
    ],
    # ...
)
```

### 2. Set Up Supabase Tables

Run these SQL commands in Supabase SQL Editor:

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT,
  tier TEXT DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking table
CREATE TABLE usage_tracking (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  date DATE,
  api_calls INTEGER DEFAULT 0,
  save_prompt_calls INTEGER DEFAULT 0,
  save_response_calls INTEGER DEFAULT 0,
  context_calls INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, date)
);

-- Indexes for performance
CREATE INDEX idx_usage_user_date ON usage_tracking(user_id, date);
CREATE INDEX idx_users_tier ON users(tier);
```

### 3. Configure Stripe Webhooks

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-backend.onrender.com/stripe/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

### 4. Test Deployment

```bash
# Health check
curl https://your-backend.onrender.com/health

# Should return:
{
  "status": "healthy",
  "version": "1.0.0",
  "memories": 0,
  "vectors": 0,
  "users": 0
}
```

## 📊 Monitoring

### Health Endpoint

Monitor with:
```bash
curl https://your-backend.onrender.com/health
```

### Admin Dashboard

Check system stats:
```bash
curl "https://your-backend.onrender.com/admin/dashboard?admin_key=your-key"
```

### Logs

**Render**: View logs in dashboard
**Railway**: `railway logs`
**Fly.io**: `flyctl logs`
**Docker**: `docker logs container-name`

## 🔒 Security Checklist

- [ ] All environment variables set
- [ ] CORS origins restricted to your domains
- [ ] Admin API key is strong and secret
- [ ] Supabase RLS policies enabled
- [ ] Stripe webhook secret configured
- [ ] HTTPS enabled (automatic on Render/Railway/Fly)
- [ ] Rate limiting active

## 🚨 Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution**: Add environment variable in deployment platform

### Issue: "Supabase connection failed"
**Solution**: Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY

### Issue: "Rate limiting not working"
**Solution**: Verify Supabase tables exist and service role key has access

### Issue: "FAISS index not persisting"
**Solution**: 
- Render: Use persistent disk (paid feature)
- Alternative: Implement S3 storage (see storage/s3_storage.py)

### Issue: "Slow cold starts"
**Solution**: 
- Render: Upgrade to paid tier for always-on
- Alternative: Use cron job to ping health endpoint every 10 minutes

## 📈 Scaling

### Horizontal Scaling

Deploy multiple instances behind load balancer:
- Use S3 for shared storage
- Use Redis for shared cache
- Use Supabase for shared state

### Vertical Scaling

Upgrade instance size:
- **Render**: Upgrade to Standard ($7/month)
- **Railway**: Increase resources
- **Fly.io**: Scale machine size

### Database Optimization

- Add indexes to Supabase tables
- Use connection pooling
- Cache frequently accessed data

## 💰 Cost Estimates

### Free Tier (Good for MVP)
- Render: Free (with limitations)
- Supabase: Free (up to 500MB)
- OpenAI: Pay per use (~$0.10/1000 requests)

### Production (1000 users)
- Render Standard: $7/month
- Supabase Pro: $25/month
- OpenAI: ~$100/month
- **Total**: ~$132/month

### Scale (10,000 users)
- Render Pro: $25/month
- Supabase Pro: $25/month
- OpenAI: ~$1000/month
- **Total**: ~$1050/month

---

*Deploy with confidence! 🚀*
