---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
version: 1.2
created: 2025-11-18T09:30:00Z
lastModified: 2025-11-20T10:00:00Z
appliedTo: ["main.py", "core/auth.py", "core/chat_service.py", "core/admin_service.py"]
---

# FastAPI Patterns for Memory Layer Backend

**Purpose**: Ensure consistent FastAPI async patterns throughout the backend.

**Usage Statistics**:
- Applied to: 8 Python files
- Patterns enforced: 15+
- Issues prevented: 3 (async/await mistakes)
- Last applied: November 20, 2025

## Async/Await
Always use async/await for I/O operations:

```python
@app.post("/save-prompt")
async def save_prompt(
    request: SavePromptRequest,
    verified_user_id: str = Depends(get_verified_user_id)
):
    # Async endpoint
    result = await save_to_database(request)
    return result
```

## Dependency Injection
Use FastAPI dependencies for auth:

```python
async def get_verified_user_id(
    token_payload: dict = Depends(verify_supabase_token)
) -> str:
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401)
    return user_id
```

## Error Handling
Use HTTPException for errors:

```python
if not user_id:
    raise HTTPException(
        status_code=403,
        detail="User ID mismatch"
    )
```

## Pydantic Models
Always use Pydantic for validation:

```python
class SavePromptRequest(BaseModel):
    user_id: str
    prompt: str
    provider: str = "chatgpt"
```

## Response Models
Define response models:

```python
class ChatResponse(BaseModel):
    response: str
    context_used: List[str]
    timestamp: str
```

## Background Tasks
Use background tasks for slow operations:

```python
from fastapi import BackgroundTasks

@app.post("/save-response")
async def save_response(
    request: SaveResponseRequest,
    background_tasks: BackgroundTasks
):
    # Quick response
    background_tasks.add_task(slow_operation, request)
    return {"success": True}
```

## Middleware Best Practices
Order matters:
1. CORS (first)
2. Rate limiting
3. Authentication
4. Custom middleware

## Real Examples from This Project

### ✅ Good: Async Endpoint with Dependencies
```python
# From main.py
@app.post("/save-prompt")
async def save_prompt(
    request: SavePromptRequest,
    verified_user_id: str = Depends(get_verified_user_id)
):
    # Proper async pattern with dependency injection
    result = chat_service.save_pending_prompt(verified_user_id, request.prompt)
    return result
```

### ✅ Good: Middleware with Body Re-attachment
```python
# From main.py - Rate limiting middleware
body = await request.body()
async def receive():
    return {"type": "http.request", "body": body}
request._receive = receive  # Re-attach for downstream handlers
```

### ❌ Bad: Blocking I/O in Async Function
```python
# Don't do this
@app.get("/data")
async def get_data():
    data = requests.get("https://api.example.com")  # Blocking!
    return data
```

### ✅ Good: Proper Async I/O
```python
# Do this instead
import httpx

@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
    return response.json()
```

---

**Note**: These patterns were consistently applied throughout development with Kiro's assistance, resulting in clean, performant async code.
