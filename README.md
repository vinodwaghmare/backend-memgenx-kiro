# Memory Layer Backend API

> Built with Kiro for Kiroween 2025 🎃

A high-performance FastAPI backend for the Memory Layer project, featuring vector search, rate limiting, and multi-tier subscriptions.

## 🎯 Features

- **Vector Search**: Semantic memory retrieval using FAISS and OpenAI embeddings
- **Multi-Tier Subscriptions**: Free, Pro, and Enterprise tiers with Stripe integration
- **Rate Limiting**: Supabase-based rate limiting per subscription tier
- **JWT Authentication**: Secure authentication with Supabase Auth
- **Admin Dashboard**: Comprehensive admin panel for user management
- **S3 Storage**: Optional AWS S3 for persistent storage
- **Async/Await**: High-performance async operations throughout

## 🏗️ Architecture

```
backend-kiro1/
├── main.py                 # FastAPI application entry point
├── core/                   # Core business logic
│   ├── config.py          # Configuration and constants
│   ├── auth.py            # JWT authentication
│   ├── chat_service.py    # Main chat orchestration
│   ├── admin_service.py   # Admin operations
│   ├── rate_limiter.py    # Rate limiting logic
│   └── llm.py             # LLM provider abstraction
├── storage/                # Data persistence
│   ├── memory_store.py    # FAISS vector store
│   └── s3_storage.py      # S3 integration
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Supabase project
- (Optional) AWS S3 bucket

### Installation

```bash
# Clone repository
git clone <repo-url>
cd backend-kiro1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your actual credentials
```

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
ADMIN_API_KEY=your-admin-key

# Optional
GEMINI_API_KEY=AI...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
AWS_ACCESS_KEY=AKIA...
AWS_SECRET_KEY=...
USE_S3_STORAGE=true
```

### Run Locally

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python main.py
```

API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Public Endpoints

- `GET /` - API information
- `GET /health` - Health check with stats

### Memory Endpoints (Requires JWT)

- `POST /save-prompt` - Save user prompt
- `POST /save-response` - Save LLM response
- `GET /context/{user_id}` - Get relevant context
- `POST /chat` - Chat with memory enhancement
- `GET /memory/{user_id}` - Get user memories
- `DELETE /memory/{user_id}` - Clear user memory

### Stripe Endpoints (Requires JWT)

- `POST /stripe/create-checkout-session` - Create checkout session
- `POST /stripe/create-portal-session` - Create customer portal
- `POST /stripe/webhook` - Handle Stripe webhooks
- `GET /stripe/subscription-status/{user_id}` - Get subscription status

### Admin Endpoints (Requires Admin Key)

- `GET /admin/dashboard` - Dashboard stats
- `GET /admin/users` - List all users
- `GET /admin/users/{user_id}` - User details
- `GET /admin/users/{user_id}/usage` - User usage stats
- `GET /admin/costs` - Cost breakdown
- `DELETE /admin/users/{user_id}` - Clear user data
- `GET /admin/health/detailed` - Detailed health check
- `POST /admin/rebuild-index` - Rebuild FAISS index

## 🔐 Authentication

All user endpoints require a valid Supabase JWT token:

```bash
curl -H "Authorization: Bearer <jwt-token>" \
  http://localhost:8000/context/user-123?query=test
```

Admin endpoints require an admin API key:

```bash
curl "http://localhost:8000/admin/dashboard?admin_key=your-admin-key"
```

## 📊 Rate Limiting

Rate limits are enforced per subscription tier:

- **Free**: 100 requests/day
- **Pro**: 1,000 requests/day
- **Enterprise**: Unlimited

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Total limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## 🗄️ Database Schema

### Supabase Tables

**users**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT,
  tier TEXT DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**usage_tracking**
```sql
CREATE TABLE usage_tracking (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  date DATE,
  api_calls INTEGER DEFAULT 0,
  save_prompt_calls INTEGER DEFAULT 0,
  save_response_calls INTEGER DEFAULT 0,
  context_calls INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🧪 Testing

```bash
# Run tests
pytest

# Test specific endpoint
python test/quick_test.py

# Test Supabase integration
python test/test_supabase_simple.py
```

## 🚢 Deployment

### Render.com

1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy!

### Docker

```bash
# Build image
docker build -t memory-layer-backend .

# Run container
docker run -p 8000:8000 --env-file .env memory-layer-backend
```

## 📝 Built with Kiro

This backend was built using Kiro's features:

### Vibe Coding
- Generated FastAPI endpoints with proper async/await patterns
- Created Pydantic models for request/response validation
- Implemented JWT authentication middleware

### Spec-Driven Development
- Followed backend-spec.md for consistent API design
- Coordinated with frontend through shared API contracts

### Agent Hooks
- Automated testing on file save
- Security vulnerability scanning
- Type synchronization with frontend

### Steering Docs
- FastAPI async patterns for high performance
- Code style guidelines for Python
- Error handling best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file

## 🎃 Kiroween 2025

Part of the Memory Layer Frankenstein project for Kiroween 2025.

**Category**: Frankenstein  
**Built with**: Kiro AI IDE

---

*Never lose context again. 🎃*
