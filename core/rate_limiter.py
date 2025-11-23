"""
Rate Limiter - Supabase-based tier limits
Built with Kiro - enforces subscription tier limits
"""
import os
from datetime import datetime, date
from supabase import create_client, Client


class RateLimiter:
    """
    Rate limiter using Supabase for tier-based limits
    
    Tiers:
    - free: 100 requests/day
    - pro: 1000 requests/day
    - enterprise: unlimited
    - admin: unlimited
    """
    
    # Tier limits
    TIER_LIMITS = {
        "free": 100,
        "pro": 1000,
        "enterprise": 999999,
        "admin": 999999
    }
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("⚠️ Supabase not configured, rate limiting disabled")
            self.supabase = None
        else:
            self.supabase = create_client(supabase_url, supabase_key)
            print("✅ Rate limiter initialized")
    
    def check_limit(self, user_id: str) -> tuple[bool, dict]:
        """
        Check if user is within rate limit
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        if not self.supabase:
            # No Supabase, allow all requests
            return True, {"tier": "free", "limit": 100, "used": 0, "remaining": 100}
        
        try:
            # Get user tier
            user_result = self.supabase.table('users').select('tier').eq('id', user_id).execute()
            
            if not user_result.data:
                # New user, default to free tier
                tier = "free"
            else:
                tier = user_result.data[0].get('tier', 'free')
            
            # Get limit for tier
            limit = self.TIER_LIMITS.get(tier, 100)
            
            # Get today's usage
            today = date.today().isoformat()
            usage_result = self.supabase.table('usage_tracking') \
                .select('api_calls') \
                .eq('user_id', user_id) \
                .eq('date', today) \
                .execute()
            
            if not usage_result.data:
                used = 0
            else:
                used = usage_result.data[0].get('api_calls', 0)
            
            # Check if within limit
            allowed = used < limit
            remaining = max(0, limit - used)
            
            # Calculate reset time (midnight UTC)
            reset_at = f"{today}T23:59:59Z"
            
            return allowed, {
                "tier": tier,
                "limit": limit,
                "used": used,
                "remaining": remaining,
                "reset_at": reset_at
            }
            
        except Exception as e:
            print(f"⚠️ Rate limit check failed: {e}")
            # Fail open - allow request
            return True, {"tier": "free", "limit": 100, "used": 0, "remaining": 100}
    
    def increment_usage(self, user_id: str, endpoint_type: str = "api_call"):
        """
        Increment usage counter for user
        
        Args:
            user_id: User identifier
            endpoint_type: Type of endpoint (api_call, save_prompt, save_response, context)
        """
        if not self.supabase:
            return
        
        try:
            today = date.today().isoformat()
            
            # Check if record exists
            result = self.supabase.table('usage_tracking') \
                .select('*') \
                .eq('user_id', user_id) \
                .eq('date', today) \
                .execute()
            
            if not result.data:
                # Create new record
                self.supabase.table('usage_tracking').insert({
                    'user_id': user_id,
                    'date': today,
                    'api_calls': 1,
                    f'{endpoint_type}_calls': 1
                }).execute()
            else:
                # Update existing record
                record_id = result.data[0]['id']
                current_calls = result.data[0].get('api_calls', 0)
                endpoint_calls = result.data[0].get(f'{endpoint_type}_calls', 0)
                
                self.supabase.table('usage_tracking').update({
                    'api_calls': current_calls + 1,
                    f'{endpoint_type}_calls': endpoint_calls + 1
                }).eq('id', record_id).execute()
                
        except Exception as e:
            print(f"⚠️ Usage increment failed: {e}")


# Global rate limiter instance
rate_limiter = RateLimiter()
