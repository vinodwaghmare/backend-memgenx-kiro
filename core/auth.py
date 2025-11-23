"""
Supabase JWT Authentication
Built with Kiro - secure authentication middleware
"""
import jwt
from fastapi import HTTPException, Depends, Header
from typing import Optional
from core.config import SUPABASE_JWT_SECRET, SUPABASE_JWT_ISSUER, SUPABASE_JWT_AUDIENCE


def verify_supabase_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI dependency to verify Supabase JWT token
    
    Args:
        authorization: Authorization header value (Bearer <token>)
        
    Returns:
        Decoded JWT payload with user information
        
    Raises:
        HTTPException(401): If token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="JWT secret not configured"
        )
    
    try:
        # Verify and decode token
        decoded = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            issuer=SUPABASE_JWT_ISSUER,
            audience=SUPABASE_JWT_AUDIENCE
        )
        
        return decoded
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}"
        )


def get_verified_user_id(token_payload: dict = Depends(verify_supabase_token)) -> str:
    """
    FastAPI dependency to extract verified user_id from token
    
    Args:
        token_payload: Decoded JWT payload from verify_supabase_token
        
    Returns:
        User ID (sub field from token)
    """
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token missing user_id (sub field)"
        )
    return user_id


def validate_path_user_id(user_id: str, verified_user_id: str = Depends(get_verified_user_id)) -> str:
    """
    FastAPI dependency to validate user_id from path parameter matches token
    
    Args:
        user_id: User ID from URL path parameter
        verified_user_id: User ID from verified JWT token
        
    Returns:
        Verified user ID
        
    Raises:
        HTTPException(403): If user IDs don't match
    """
    if user_id != verified_user_id:
        raise HTTPException(
            status_code=403,
            detail="User ID mismatch - token user does not match request user"
        )
    return verified_user_id
