# API Reference

Complete API documentation for Memory Layer Backend.

## Base URL

```
Production: https://your-backend.onrender.com
Local: http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication from Supabase.

### Headers

```http
Authorization: Bearer <jwt-token>
```

Get JWT token from Supabase Auth after user login.

---

## Public Endpoints

### GET /

Get API information.

**Response:**
```json
{
  "message": "Memory Layer API - Universal Context Memory System",
  "version": "1.0.0",
  "category": "Frankenstein",
  "built_with": "Kiro",
  "features": [...],
  "endpoints": {...}
}
```

### GET /health

Health check with system stats.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "memories": 1234,
  "vectors": 1234,
  "users": 42,
  "storage": "Local"
}
```

---

## Memory Endpoints

### POST /save-prompt

Save user prompt immediately (before LLM response).

**Authentication:** Required

**Request:**
```json
{
  "user_id": "user-uuid",
  "prompt": "What is the capital of France?",
  "provider": "chatgpt"
}
```

**Response:**
```json
{
  "success": true,
  "chunks_stored": 1,
  "user_id": "user-uuid",
  "prompt": "What is the capital of France?",
  "provider": "chatgpt",
  "timestamp": "2025-11-22T10:30:00Z"
}
```

**Rate Limit:** Counts toward daily limit

### POST /save-response

Save LLM response after generation.

**Authentication:** Required

**Request:**
```json
{
  "user_id": "user-uuid",
  "prompt": "What is the capital of France?",
  "response": "The capital of France is Paris.",
  "provider": "openai"
}
```

**Response:**
```json
{
  "success": true,
  "chunks_stored": 1,
  "user_id": "user-uuid",
  "timestamp": "2025-11-22T10:30:05Z"
}
```

**Rate Limit:** Counts toward daily limit

### GET /context/{user_id}

Get relevant context for a query.

**Authentication:** Required

**Parameters:**
- `user_id` (path): User identifier
- `query` (query): Search query
- `top_k` (query, optional): Number of results (default: 5)

**Example:**
```http
GET /context/user-123?query=France&top_k=3
Authorization: Bearer <token>
```

**Response:**
```json
{
  "contexts": [
    "User: What is the capital of France?\nAssistant: The capital of France is Paris.",
    "User: Tell me about French cuisine...",
    "User: What language is spoken in France?..."
  ],
  "count": 3
}
```

**Rate Limit:** Counts toward daily limit

### POST /chat

Chat with memory enhancement.

**Authentication:** Optional (but recommended)

**Request:**
```json
{
  "user_id": "user-uuid",
  "message": "What did I ask about France?",
  "llm_provider": "openai",
  "top_k": 20
}
```

**Response:**
```json
{
  "response": "You asked about the capital of France, which is Paris.",
  "context_used": ["User: What is the capital of France?..."],
  "timestamp": "2025-11-22T10:30:10Z"
}
```

### GET /memory/{user_id}

Get all memories for a user.

**Authentication:** Optional

**Response:**
```json
{
  "user_id": "user-uuid",
  "memories": [
    {
      "user_message": "What is the capital of France?",
      "llm_response": "The capital of France is Paris.",
      "chunk_text": "User: What is...",
      "timestamp": "2025-11-22T10:30:00Z",
      "provider": "openai"
    }
  ],
  "count": 1
}
```

### DELETE /memory/{user_id}

Clear all memories for a user.

**Authentication:** Optional

**Response:**
```json
{
  "message": "Cleared 42 memories",
  "cleared": 42
}
```

---

## Admin Endpoints

All admin endpoints require `admin_key` query parameter.

### GET /admin/dashboard

Get admin dashboard stats.

**Parameters:**
- `admin_key` (query): Admin API key

**Example:**
```http
GET /admin/dashboard?admin_key=your-admin-key
```

**Response:**
```json
{
  "system": {
    "total_users": 42,
    "total_memories": 1234,
    "total_vectors": 1234,
    "storage_type": "Local",
    "health_score": 100
  },
  "usage": {
    "api_calls_today": 567,
    "memories_stored_today": 89,
    "active_users_today": 23
  },
  "timestamp": "2025-11-22T10:30:00Z"
}
```

### GET /admin/users

Get list of all users.

**Parameters:**
- `admin_key` (query): Admin API key
- `sort_by` (query, optional): Sort by 'memories', 'last_active', or 'tier'
- `limit` (query, optional): Max users to return

**Example:**
```http
GET /admin/users?admin_key=your-key&sort_by=memories&limit=10
```

**Response:**
```json
{
  "users": [
    {
      "user_id": "user-uuid",
      "memory_count": 156,
      "last_active": "2025-11-22T10:30:00Z",
      "tier": "pro"
    }
  ],
  "count": 10,
  "sort_by": "memories"
}
```

### GET /admin/users/{user_id}

Get detailed stats for a specific user.

**Parameters:**
- `user_id` (path): User identifier
- `admin_key` (query): Admin API key

**Response:**
```json
{
  "user_id": "user-uuid",
  "memory_count": 156,
  "recent_memories": [...],
  "first_memory": "2025-10-01T10:00:00Z",
  "last_memory": "2025-11-22T10:30:00Z"
}
```

### DELETE /admin/users/{user_id}

Clear all data for a user.

**Parameters:**
- `user_id` (path): User identifier
- `admin_key` (query): Admin API key

**Response:**
```json
{
  "success": true,
  "user_id": "user-uuid",
  "memories_cleared": 156,
  "timestamp": "2025-11-22T10:30:00Z"
}
```

---

## Rate Limiting

### Headers

All responses include rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 2025-11-22T23:59:59Z
```

### Limits by Tier

- **Free**: 100 requests/day
- **Pro**: 1,000 requests/day
- **Enterprise**: Unlimited
- **Admin**: Unlimited

### Rate Limit Exceeded

**Status Code:** 429 Too Many Requests

**Response:**
```json
{
  "error": "Rate limit exceeded",
  "message": "You've reached your daily limit of 100 requests",
  "tier": "free",
  "limit": 100,
  "used": 100,
  "remaining": 0,
  "reset_at": "2025-11-22T23:59:59Z",
  "upgrade_url": "https://yoursaas.com/pricing"
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "error": "user_id and prompt required"
}
```

### 401 Unauthorized

```json
{
  "success": false,
  "error": "Missing Authorization header"
}
```

### 403 Forbidden

```json
{
  "success": false,
  "error": "User ID mismatch"
}
```

### 404 Not Found

```json
{
  "success": false,
  "error": "User not found"
}
```

### 429 Too Many Requests

See Rate Limiting section above.

### 500 Internal Server Error

```json
{
  "success": false,
  "error": "Internal server error message"
}
```

---

## Code Examples

### Python

```python
import requests

# Save prompt
response = requests.post(
    "https://your-backend.onrender.com/save-prompt",
    headers={"Authorization": f"Bearer {jwt_token}"},
    json={
        "user_id": "user-123",
        "prompt": "What is AI?",
        "provider": "chatgpt"
    }
)
print(response.json())
```

### JavaScript

```javascript
// Get context
const response = await fetch(
  `https://your-backend.onrender.com/context/user-123?query=AI&top_k=5`,
  {
    headers: {
      'Authorization': `Bearer ${jwtToken}`
    }
  }
);
const data = await response.json();
console.log(data.contexts);
```

### cURL

```bash
# Health check
curl https://your-backend.onrender.com/health

# Save response (with auth)
curl -X POST https://your-backend.onrender.com/save-response \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "prompt": "What is AI?",
    "response": "AI stands for Artificial Intelligence...",
    "provider": "openai"
  }'
```

---

## OpenAPI/Swagger

Interactive API documentation available at:

```
https://your-backend.onrender.com/docs
```

Alternative ReDoc documentation:

```
https://your-backend.onrender.com/redoc
```

---

*Complete API reference for Memory Layer Backend 🎃*
