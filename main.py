"""
Memory Layer Backend API
Built with Kiro for Kiroween 2025 🎃

FastAPI application with vector search, rate limiting, and multi-tier subscriptions.
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Core imports
from core.chat_service import ChatService
from core.auth import get_verified_user_id, validate_path_user_id
from core.admin_service import AdminService
from core.rate_limiter import rate_limiter
from core.config import STRIPE_WEBHOOK_SECRET

# Initialize FastAPI
app = FastAPI(
    title="Memory Layer API",
    description="High-performance backend for universal context memory",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Format HTTP exceptions consistently"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware - checks Supabase for tier-based limits
    
    Protected endpoints: /save-prompt, /save-response, /context/{user_id}
    Skipped: /admin/*, /stripe/*, /health, /
    """
    # Skip rate limiting for certain endpoints
    if (request.method == "OPTIONS" or
        request.url.path.startswith("/admin") or
        request.url.path.startswith("/stripe") or
        request.url.path in ["/health", "/"]):
        return await call_next(request)
    
    # Extract user_id from request
    user_id = None
    
    try:
        # Try to get from request body (POST requests)
        if request.method == "POST":
            body = await request.body()
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
            
            try:
                import json
                data = json.loads(body.decode())
                user_id = data.get("user_id")
            except:
                pass
        
        # Get from path parameter (GET requests like /context/{user_id})
        elif "/context/" in request.url.path:
            parts = request.url.path.split("/")
            if len(parts) >= 3 and parts[1] == "context":
                user_id = parts[2]
    
    except Exception as e:
        print(f"WARNING: Failed to extract user_id: {e}")
    
    # If no user_id found, allow request (fail open)
    if not user_id:
        return await call_next(request)
    
    # Check rate limit
    allowed, info = rate_limiter.check_limit(user_id)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"You've reached your daily limit of {info.get('limit')} requests",
                "tier": info.get("tier"),
                "limit": info.get("limit"),
                "used": info.get("used"),
                "remaining": 0,
                "reset_at": info.get("reset_at"),
                "upgrade_url": "https://yoursaas.com/pricing"
            },
            headers={
                "X-RateLimit-Limit": str(info.get("limit", 0)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info.get("reset_at", "")),
                "Retry-After": "3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(info.get("limit", 0))
    response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
    response.headers["X-RateLimit-Reset"] = str(info.get("reset_at", ""))
    
    # Increment usage after successful request
    if response.status_code < 400:
        endpoint_type = "api_call"
        if "/save-prompt" in request.url.path:
            endpoint_type = "save_prompt"
        elif "/save-response" in request.url.path:
            endpoint_type = "save_response"
        elif "/context" in request.url.path:
            endpoint_type = "context"
        
        try:
            rate_limiter.increment_usage(user_id, endpoint_type)
        except Exception as e:
            print(f"WARNING: Failed to increment usage: {e}")
    
    return response

# Initialize services
chat_service = ChatService()
admin_service = AdminService(chat_service)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SavePromptRequest(BaseModel):
    user_id: str
    prompt: str
    provider: str = "chatgpt"

class SaveResponseRequest(BaseModel):
    user_id: str
    prompt: str
    response: str
    provider: str = "openai"

class ChatRequest(BaseModel):
    user_id: str
    message: str
    llm_provider: str = "openai"
    top_k: int = 20

class ChatResponse(BaseModel):
    response: str
    context_used: List[str]
    timestamp: str

# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Memory Layer API - Universal Context Memory System",
        "version": "1.0.0",
        "category": "Frankenstein",
        "built_with": "Kiro",
        "features": [
            "Vector search with FAISS",
            "Multi-tier subscriptions",
            "Rate limiting per tier",
            "JWT authentication",
            "Admin dashboard",
            "S3 persistence"
        ],
        "endpoints": {
            "memory": ["/save-prompt", "/save-response", "/context/{user_id}"],
            "admin": ["/admin/dashboard", "/admin/users"],
            "health": ["/health"]
        }
    }

@app.get("/health")
async def health():
    """Health check with system stats"""
    stats = chat_service.get_stats()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "memories": stats["total_memories"],
        "vectors": stats["total_vectors"],
        "users": stats["total_users"],
        "storage": stats.get("storage_type", "Local")
    }

# ============================================================================
# MEMORY ENDPOINTS (Requires JWT)
# ============================================================================

@app.post("/save-prompt")
async def save_prompt(
    request: SavePromptRequest,
    verified_user_id: str = Depends(get_verified_user_id)
):
    """
    Save user prompt immediately (before LLM response)
    
    Called by Chrome extension when user submits prompt.
    """
    try:
        if not request.user_id or not request.prompt:
            raise HTTPException(status_code=400, detail="user_id and prompt required")
        
        # Validate user_id matches token
        if request.user_id != verified_user_id:
            raise HTTPException(
                status_code=403,
                detail="User ID mismatch"
            )
        
        # Store prompt as pending
        chat_service.save_pending_prompt(verified_user_id, request.prompt)
        
        return {
            "success": True,
            "chunks_stored": 1,
            "user_id": verified_user_id,
            "prompt": request.prompt,
            "provider": request.provider,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Save prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-response")
async def save_response(
    request: SaveResponseRequest,
    verified_user_id: str = Depends(get_verified_user_id)
):
    """
    Save LLM response after generation
    
    Called by Chrome extension after capturing LLM response.
    """
    try:
        if not request.user_id or not request.prompt or not request.response:
            raise HTTPException(
                status_code=400,
                detail="user_id, prompt, and response required"
            )
        
        # Validate user_id matches token
        if request.user_id != verified_user_id:
            raise HTTPException(
                status_code=403,
                detail="User ID mismatch"
            )
        
        # Store complete conversation
        result = chat_service.save_conversation(
            user_id=verified_user_id,
            user_message=request.prompt,
            llm_response=request.response,
            provider=request.provider
        )
        
        return {
            "success": True,
            "chunks_stored": result.get("chunks_stored", 0),
            "user_id": verified_user_id,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Save response error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/context/{user_id}")
async def get_context(
    user_id: str,
    query: str,
    top_k: int = 5,
    verified_user_id: str = Depends(validate_path_user_id)
):
    """
    Get relevant context for a query WITHOUT generating response
    
    Used by Chrome extension to enhance prompts before submission.
    """
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Use verified user_id for security
        contexts = chat_service.retrieve_context(verified_user_id, query, top_k)
        
        return {
            "contexts": contexts,
            "count": len(contexts)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Context retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with memory enhancement"""
    try:
        if not request.user_id or not request.message:
            raise HTTPException(status_code=400, detail="Invalid input")
        
        result = chat_service.chat(
            user_id=request.user_id,
            message=request.message,
            llm_provider=request.llm_provider,
            top_k=request.top_k
        )
        
        return ChatResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/{user_id}")
async def get_memory(user_id: str):
    """Get user memories"""
    memories = chat_service.get_user_memories(user_id)
    return {
        "user_id": user_id,
        "memories": memories,
        "count": len(memories)
    }

@app.delete("/memory/{user_id}")
async def clear_memory(user_id: str):
    """Clear user memory"""
    cleared = chat_service.clear_user_data(user_id)
    return {
        "message": f"Cleared {cleared} memories" if cleared > 0 else "No memories found",
        "cleared": cleared
    }

# ============================================================================
# ADMIN ENDPOINTS (Requires Admin Key)
# ============================================================================

def verify_admin_key(admin_key: str = None):
    """Verify admin API key"""
    import os
    expected_key = os.getenv("ADMIN_API_KEY", "admin-key-2025")
    if admin_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")

@app.get("/admin/dashboard")
async def get_admin_dashboard(admin_key: str = None):
    """Get admin dashboard stats"""
    verify_admin_key(admin_key)
    
    try:
        stats = admin_service.get_dashboard_stats()
        return stats
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/users")
async def get_admin_users(
    admin_key: str = None,
    sort_by: str = "cost",
    limit: Optional[int] = None
):
    """Get list of all users with stats"""
    verify_admin_key(admin_key)
    
    try:
        users = admin_service.get_users_list(sort_by=sort_by, limit=limit)
        return {
            "users": users,
            "count": len(users),
            "sort_by": sort_by
        }
    except Exception as e:
        print(f"❌ Users list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/users/{user_id}")
async def get_admin_user_details(user_id: str, admin_key: str = None):
    """Get detailed stats for a specific user"""
    verify_admin_key(admin_key)
    
    try:
        details = admin_service.get_user_details(user_id)
        if not details:
            raise HTTPException(status_code=404, detail="User not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ User details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🎃 Memory Layer Backend API")
    print("="*60)
    print("Built with Kiro for Kiroween 2025")
    print("Category: Frankenstein")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
