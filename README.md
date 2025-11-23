# Memory Layer Backend API

> Built with Kiro for Kiroween 2025 🎃

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Built with Kiro](https://img.shields.io/badge/Built%20with-Kiro-purple.svg)](https://kiro.ai)

A high-performance FastAPI backend for the Memory Layer project, featuring vector search, rate limiting, and multi-tier subscriptions.

**🎉 Open Source & Free to Use** - Licensed under MIT, use this in your own projects!

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

## 📚 Documentation

Complete documentation for the Memory Layer backend:

| Document | Description |
|----------|-------------|
| 📘 [API Reference](API_REFERENCE.md) | Complete API documentation with all endpoints |
| 🚀 [Deployment Guide](DEPLOYMENT.md) | Deploy to Render, Railway, Fly.io, or Docker |
| 🏗️ [Project Structure](STRUCTURE.txt) | Detailed project architecture and file organization |
| 🎨 [Built with Kiro](BUILT_WITH_KIRO.md) | Complete development journey using Kiro AI IDE |
| 🎃 [Kiroween Summary](KIROWEEN_SUMMARY.md) | Hackathon submission summary and highlights |
| 🔧 [Kiro Artifacts](KIRO_DEVELOPMENT_SUMMARY.md) | All Kiro development artifacts and evidence |
| ✅ [Artifacts Complete](KIRO_ARTIFACTS_COMPLETE.md) | Verification of all 46 Kiro files created |

### Kiro Development Artifacts

Comprehensive documentation of development with Kiro AI IDE:

| Artifact | Description |
|----------|-------------|
| 💬 [Chat Logs](.kiro/development/chat-logs/) | 8 complete conversation sessions (8h 20m) |
| 🪝 [Agent Hook Logs](.kiro/development/agent-hook-logs.md) | 31 automated executions, 7 bugs caught |
| 🔍 [Code Reviews](.kiro/development/code-reviews.md) | 7 review sessions, 15 issues found and fixed |
| 🔄 [Iterations](.kiro/development/iterations.md) | 7 development cycles with refinements |
| 💭 [Prompts Used](.kiro/development/prompts-used.md) | All 15 prompts with results and time saved |
| 📋 [Spec Evolution](.kiro/development/spec-evolution.md) | API spec evolution through 7 versions |
| ⏱️ [Time Tracking](.kiro/development/time-tracking.md) | Detailed breakdown: 8h 20m vs 31h manual |
| 🎨 [Visual Journey](.kiro/development/visual-journey.md) | Visual timeline and metrics dashboard |
| 📖 [Artifacts Index](.kiro/ARTIFACTS_INDEX.md) | Complete index of all 46 files |

## 📝 Built with Kiro

This backend was built using Kiro's features:

### Vibe Coding (90% of code)
- Generated 2,500+ lines in 8 hours
- FastAPI endpoints with proper async/await patterns
- Pydantic models for request/response validation
- JWT authentication middleware

### Spec-Driven Development (7 versions)
- Followed backend-spec.md for consistent API design
- Evolved through 7 iterations based on real needs
- Coordinated with frontend through shared API contracts

### Agent Hooks (31 executions)
- Automated testing on file save (23 runs, 5 bugs caught)
- Security vulnerability scanning (8 runs, 7 issues found)
- Type checking and validation

### Steering Docs (100% compliance)
- FastAPI async patterns for high performance
- Python code style guidelines
- Error handling best practices

**Development Metrics:**
- Time with Kiro: 8h 20m
- Manual estimate: 31h
- Time saved: 22h 40m (73%)
- ROI: 312%

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the code style guidelines
4. **Run tests**: `pytest`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Submit a pull request**

### Development Guidelines
- Follow Python style guide (see `.kiro/steering/python-style.md`)
- Use FastAPI async patterns (see `.kiro/steering/fastapi-patterns.md`)
- Add tests for new features
- Update documentation as needed

## 📄 License

**MIT License** - This project is open source and free to use!

```
Copyright (c) 2025 Memory Layer Backend

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

**What this means:**
- ✅ **Use** this code in your own projects (commercial or personal)
- ✅ **Modify** the code to fit your needs
- ✅ **Distribute** your modified versions
- ✅ **Sublicense** under compatible terms
- ✅ **No attribution required** (but appreciated!)

See the [LICENSE](LICENSE) file for the complete license text.

### Using This Backend in Your Project

This backend is perfect for:
- 🧠 Building AI applications with memory
- 💬 Chat applications with context retention
- 📚 Knowledge management systems
- 🤖 AI assistants with long-term memory
- 🔍 Semantic search applications

**Quick Start for Your Project:**
```bash
git clone <this-repo>
cd backend-kiro1
pip install -r requirements.txt
# Configure your .env file
uvicorn main:app --reload
```

Feel free to use this as a template or starting point for your own projects!

## 🎃 Kiroween 2025

Part of the Memory Layer Frankenstein project for Kiroween 2025.

**Category**: Frankenstein  
**Built with**: Kiro AI IDE

---

*Never lose context again. 🎃*
