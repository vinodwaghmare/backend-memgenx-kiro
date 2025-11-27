# Backend API Design Document

**Feature**: Memory Layer Backend API  
**Status**: ✅ Implemented  
**Built with**: Kiro IDE

## Architecture Overview

### System Architecture

```
┌─────────────────┐
│ Chrome Extension│
└────────┬────────┘
         │ HTTPS/JWT
         ▼
┌─────────────────┐
│   FastAPI App   │
│  (main.py)      │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
│ Auth   │ │ Rate │ │ Memory │ │Admin │
│Service │ │Limiter│ │Store   │ │Panel │
└────────┘ └──────┘ └───┬────┘ └──────┘
                        │
                   ┌────┴────┐
                   ▼         ▼
              ┌─────────┐ ┌──────┐
              │Supabase │ │FAISS │
              │PostgreSQL│ │Vector│
              └─────────┘ └──────┘
```

### Component Design

#### 1. Core Components

**main.py** - FastAPI Application
- Handles HTTP routing
- Middleware configuration
- CORS setup
- Error handling

**core/auth.py** - Authentication Service
- JWT token validation
- Supabase integration
- User verification
- Token refresh logic

**core/rate_limiter.py** - Rate Limiting
- Tier-based limits (Free/Pro/Enterprise)
- Redis-backed counters
- Sliding window algorithm
- Graceful degradation

**storage/memory_store.py** - Memory Storage
- FAISS vector indexing
- Supabase persistence
- Chunking strategy
- Semantic search

**core/chat_service.py** - Chat Integration
- LLM response handling
- Context injection
- Prompt formatting
- Provider abstraction

**core/admin_service.py** - Admin Dashboard
- System statistics
- Health monitoring
- User analytics
- Performance metrics

#### 2. Data Models

**Memory Model**
```python
class Memory:
    id: str
    user_id: str
    prompt: str
    response: str
    provider: str  # chatgpt, claude, gemini, grok
    timestamp: datetime
    embedding: List[float]
    metadata: dict
```

**User Tier Model**
```python
class UserTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
```

**Rate Limit Model**
```python
class RateLimit:
    user_id: str
    tier: UserTier
    requests_today: int
    limit: int
    reset_at: datetime
```

### Design Decisions

#### DD-1: Split Save Endpoints
**Decision**: Separate `/save-prompt` and `/save-response` endpoints  
**Rationale**: Chrome extension needs to save prompts immediately before AI responds  
**Alternatives Considered**: Single endpoint with optional response field  
**Trade-offs**: More endpoints but better UX and reliability

#### DD-2: FAISS for Vector Search
**Decision**: Use FAISS instead of pgvector  
**Rationale**: 10x faster for < 100K vectors, easier to deploy  
**Alternatives Considered**: pgvector, Pinecone, Weaviate  
**Trade-offs**: In-memory storage but acceptable for MVP

#### DD-3: Async/Await Throughout
**Decision**: Use async/await for all I/O operations  
**Rationale**: Better concurrency, handles 1000+ concurrent users  
**Alternatives Considered**: Sync operations with threading  
**Trade-offs**: More complex code but much better performance

#### DD-4: JWT from Supabase
**Decision**: Delegate authentication to Supabase  
**Rationale**: Don't reinvent auth, leverage Supabase's security  
**Alternatives Considered**: Custom JWT, OAuth2  
**Trade-offs**: Vendor lock-in but saves development time

#### DD-5: Tier-Based Rate Limiting
**Decision**: Implement three tiers with different limits  
**Rationale**: Monetization strategy, prevent abuse  
**Alternatives Considered**: Single rate limit for all  
**Trade-offs**: More complexity but enables business model

### API Design Patterns

#### Pattern 1: Consistent Response Format
All endpoints return:
```python
{
    "success": bool,
    "data": dict | None,
    "error": str | None
}
```

#### Pattern 2: Dependency Injection
```python
async def endpoint(
    user: User = Depends(get_current_user),
    limiter: RateLimiter = Depends(get_rate_limiter)
):
    # Endpoint logic
```

#### Pattern 3: Error Handling
```python
try:
    result = await operation()
    return {"success": True, "data": result}
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {"success": False, "error": str(e)}
```

### Database Schema

#### memories table
```sql
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    prompt TEXT NOT NULL,
    response TEXT,
    provider VARCHAR(50) NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_memories ON memories(user_id, created_at DESC);
CREATE INDEX idx_provider ON memories(provider);
```

#### rate_limits table
```sql
CREATE TABLE rate_limits (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    tier VARCHAR(20) NOT NULL DEFAULT 'free',
    requests_today INT DEFAULT 0,
    reset_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Security Design

#### Authentication Flow
1. Extension sends JWT in Authorization header
2. FastAPI validates token with Supabase
3. Extract user_id from token claims
4. Check rate limits for user
5. Process request if authorized

#### Rate Limiting Strategy
- Sliding window per user per day
- Reset at midnight UTC
- Graceful degradation on Redis failure
- Clear error messages with retry-after

#### Data Protection
- All data encrypted at rest (Supabase)
- JWT tokens expire after 24 hours
- Admin endpoints require separate API key
- No PII in logs

### Performance Optimizations

#### PO-1: Connection Pooling
- Supabase connection pool: 10-50 connections
- Reuse connections across requests
- Automatic reconnection on failure

#### PO-2: Vector Search Caching
- Cache FAISS index in memory
- Rebuild index every 5 minutes
- Fallback to database on cache miss

#### PO-3: Async Operations
- All I/O operations are async
- Concurrent request handling
- Non-blocking database queries

#### PO-4: Response Compression
- Gzip compression for responses > 1KB
- Reduces bandwidth by 70%
- Automatic in FastAPI

### Monitoring & Observability

#### Metrics Tracked
- Request count per endpoint
- Response time percentiles (p50, p95, p99)
- Error rate by type
- Rate limit hits
- Memory usage
- Database connection pool status

#### Logging Strategy
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request ID for tracing
- No sensitive data in logs

#### Health Checks
- `/health` endpoint
- Database connectivity
- FAISS index status
- Memory usage
- Response time

### Deployment Architecture

#### Render.com Configuration
- **Service Type**: Web Service
- **Environment**: Python 3.11
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Auto-deploy**: On git push to main
- **Health Check**: `/health` endpoint

#### Environment Variables
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
ADMIN_API_KEY=xxx
OPENAI_API_KEY=xxx
ENVIRONMENT=production
```

### Error Handling Strategy

#### Error Categories
1. **Client Errors (4xx)**
   - 400: Bad Request (invalid input)
   - 401: Unauthorized (invalid token)
   - 403: Forbidden (rate limit exceeded)
   - 404: Not Found (resource doesn't exist)

2. **Server Errors (5xx)**
   - 500: Internal Server Error
   - 503: Service Unavailable (database down)

#### Error Response Format
```json
{
    "success": false,
    "error": "Human-readable error message",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "details": {
        "limit": 100,
        "reset_at": "2025-11-21T00:00:00Z"
    }
}
```

### Testing Strategy

#### Unit Tests
- Test each service independently
- Mock external dependencies
- 85%+ code coverage

#### Integration Tests
- Test API endpoints end-to-end
- Use test database
- Verify rate limiting

#### Load Tests
- Simulate 1000 concurrent users
- Verify response times < 500ms
- Check for memory leaks

### Future Enhancements

#### Phase 2 Features
- Real-time WebSocket updates
- Memory sharing between users
- Advanced analytics dashboard
- Multi-language support

#### Scalability Improvements
- Horizontal scaling with load balancer
- Distributed FAISS index
- Redis cluster for rate limiting
- CDN for static assets

---

## Correctness Properties

### CP-1: Authentication Integrity
**Property**: All authenticated requests must have valid JWT tokens  
**Verification**: Token validation middleware on all protected endpoints  
**Test**: Attempt requests with invalid/expired tokens → 401 error

### CP-2: Rate Limit Enforcement
**Property**: Users cannot exceed their tier's rate limit  
**Verification**: Rate limiter checks before processing requests  
**Test**: Send 101 requests as free user → 403 error on 101st

### CP-3: Data Isolation
**Property**: Users can only access their own memories  
**Verification**: All queries filtered by user_id from JWT  
**Test**: Attempt to access another user's memory → 403 error

### CP-4: Vector Search Accuracy
**Property**: Search results must be semantically relevant  
**Verification**: FAISS cosine similarity > 0.7 threshold  
**Test**: Search for "Python code" → returns Python-related memories

### CP-5: Response Time SLA
**Property**: 95% of requests complete within 500ms  
**Verification**: Monitoring and alerting on p95 latency  
**Test**: Load test with 1000 concurrent users → p95 < 500ms

---

**Built with Kiro using:**
- Spec-Driven Development for architecture
- Vibe Coding for implementation
- Agent Hooks for validation
- Steering Docs for consistency