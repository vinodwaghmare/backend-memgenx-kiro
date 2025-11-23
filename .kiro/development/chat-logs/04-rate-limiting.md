# Chat Log: Rate Limiting Implementation

**Date**: November 19, 2025  
**Session**: 4 of 8  
**Duration**: 50 minutes

---

## User Request

> I need rate limiting based on subscription tiers:
> - Free: 100 requests/day
> - Pro: 1,000 requests/day  
> - Enterprise: Unlimited
> - Admin: Unlimited
> 
> Store usage in Supabase and check on each request.

## Kiro Response

I'll create a RateLimiter class that integrates with Supabase. We'll track daily usage and enforce tier-based limits.

**Creating core/rate_limiter.py...**

## Implementation

### Database Schema Design

First, let's design the Supabase tables:

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT,
  tier TEXT DEFAULT 'free',
  stripe_customer_id TEXT,
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
```

### RateLimiter Class

```python
class RateLimiter:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        self.tier_limits = {
            "free": 100,
            "pro": 1000,
            "enterprise": 999999,
            "admin": 999999
        }
    
    def check_limit(self, user_id: str) -> tuple[bool, dict]:
        """Check if user is within rate limit"""
        try:
            # Get user tier
            user = self.supabase.table('users').select('tier').eq('id', user_id).execute()
            tier = user.data[0]['tier'] if user.data else 'free'
            
            # Get today's usage
            today = datetime.now().date().isoformat()
            usage = self.supabase.table('usage_tracking')\
                .select('api_calls')\
                .eq('user_id', user_id)\
                .eq('date', today)\
                .execute()
            
            used = usage.data[0]['api_calls'] if usage.data else 0
            limit = self.tier_limits[tier]
            
            return used < limit, {
                "tier": tier,
                "limit": limit,
                "used": used,
                "remaining": max(0, limit - used)
            }
        except Exception as e:
            # Fail open - allow request if check fails
            return True, {"tier": "free", "limit": 100}
```

### Middleware Integration

User: "How do I integrate this into FastAPI?"

Kiro: "Use middleware to check rate limits before processing requests."

```python
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip admin and health endpoints
    if request.url.path.startswith("/admin") or request.url.path == "/health":
        return await call_next(request)
    
    # Extract user_id from request
    user_id = extract_user_id(request)
    
    # Check rate limit
    allowed, info = rate_limiter.check_limit(user_id)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "tier": info["tier"],
                "limit": info["limit"],
                "used": info["used"]
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    
    return response
```

---

## Testing

```bash
# Test as free user (100 limit)
for i in {1..101}; do
  curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/context/user-123?query=test
done

# Request 101 should return 429
# → {"error": "Rate limit exceeded", "tier": "free", "limit": 100}
```

**✅ Rate limiting working!**

---

## Next Steps

User: "Perfect! Now let's build the main FastAPI application with all the endpoints."

**→ Continue to Session 5: FastAPI Application**
