---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# FastAPI Async Patterns for Memory Layer

## Core Principles
- Use async/await for all I/O operations (database, HTTP, file system)
- Use sync functions only for CPU-bound operations
- Never block the event loop with time.sleep() or blocking I/O

## Database Operations

### Async Database Queries
```python
from supabase import create_client, Client
import asyncio

# Use async client
async def get_memories(user_id: str) -> list[Memory]:
    # Supabase client operations
    response = await asyncio.to_thread(
        supabase.table('memories')
        .select('*')
        .eq('user_id', user_id)
        .execute
    )
    return response.data
```

### Connection Pooling
```python
# Use connection pool for better performance
from asyncpg import create_pool

pool = await create_pool(
    dsn=DATABASE_URL,
    min_size=10,
    max_size=20
)

async def query_db(sql: str, *args):
    async with pool.acquire() as conn:
        return await conn.fetch(sql, *args)
```

## Dependency Injection

### Async Dependencies
```python
from fastapi import Depends

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract user from JWT token."""
    payload = jwt.decode(token, SECRET_KEY)
    user = await get_user_by_id(payload['sub'])
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get('/api/memories')
async def list_memories(
    user: User = Depends(get_current_user)
) -> list[Memory]:
    return await get_user_memories(user.id)
```

## Error Handling

### Structured Error Responses
```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    detail: str
    request_id: str

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error='Internal Server Error',
            detail=str(exc),
            request_id=request.state.request_id
        ).dict()
    )
```

### Custom Exceptions
```python
class QuotaExceededError(Exception):
    """Raised when user exceeds their memory quota."""
    pass

@app.exception_handler(QuotaExceededError)
async def quota_exceeded_handler(request: Request, exc: QuotaExceededError):
    return JSONResponse(
        status_code=429,
        content={'error': 'Quota exceeded', 'detail': str(exc)}
    )
```

## Background Tasks

### Using BackgroundTasks
```python
from fastapi import BackgroundTasks

async def generate_embedding(memory_id: str):
    """Generate vector embedding for memory (slow operation)."""
    memory = await get_memory(memory_id)
    embedding = await openai.embeddings.create(
        input=memory.content,
        model='text-embedding-ada-002'
    )
    await update_memory_embedding(memory_id, embedding)

@app.post('/api/memories')
async def create_memory(
    memory: MemoryCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    # Create memory immediately
    new_memory = await insert_memory(memory, user.id)
    
    # Generate embedding in background
    background_tasks.add_task(generate_embedding, new_memory.id)
    
    return new_memory
```

## Rate Limiting

### Async Rate Limiter
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post('/api/memories')
@limiter.limit('100/day')
async def create_memory(request: Request, memory: MemoryCreate):
    # Check user-specific quota
    user = await get_current_user(request)
    if user.quota_used >= user.quota_limit:
        raise QuotaExceededError(f'Daily limit of {user.quota_limit} reached')
    
    # Create memory
    return await insert_memory(memory, user.id)
```

## Caching

### Redis Caching
```python
import aioredis

redis = await aioredis.create_redis_pool('redis://localhost')

async def get_user_memories_cached(user_id: str) -> list[Memory]:
    # Try cache first
    cached = await redis.get(f'memories:{user_id}')
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    memories = await get_memories(user_id)
    
    # Cache for 5 minutes
    await redis.setex(
        f'memories:{user_id}',
        300,
        json.dumps([m.dict() for m in memories])
    )
    
    return memories
```

## Testing Async Code

### Pytest Async
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_memory():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post(
            '/api/memories',
            json={'content': 'Test memory', 'url': 'https://example.com'},
            headers={'Authorization': 'Bearer test-token'}
        )
        assert response.status_code == 201
        assert response.json()['content'] == 'Test memory'
```

## Performance Tips
- Use `asyncio.gather()` for concurrent operations
- Implement connection pooling for databases
- Cache frequently accessed data
- Use background tasks for slow operations
- Monitor with async-friendly profilers

---

*These patterns ensure high-performance async operations in the Memory Layer backend.*
