"""
Admin Service - User management and analytics
Built with Kiro - comprehensive admin operations
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class AdminService:
    """
    Admin operations for user management and system analytics
    """
    
    def __init__(self, chat_service):
        self.chat_service = chat_service
        self.store = chat_service.store
    
    def get_dashboard_stats(self) -> dict:
        """
        Get admin dashboard overview stats
        
        Returns:
            System stats, usage stats, and health metrics
        """
        stats = self.store.get_stats()
        
        # Calculate additional metrics
        users = self._get_all_users()
        total_users = len(users)
        
        return {
            "system": {
                "total_users": total_users,
                "total_memories": stats["total_memories"],
                "total_vectors": stats["total_vectors"],
                "storage_type": stats.get("storage_type", "Local"),
                "health_score": 100 if stats["total_vectors"] == stats["total_memories"] else 90
            },
            "usage": {
                "api_calls_today": 0,  # Would query from usage_tracking
                "memories_stored_today": 0,
                "active_users_today": 0
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_users_list(self, sort_by: str = "memories", limit: Optional[int] = None) -> List[dict]:
        """
        Get list of all users with their stats
        
        Args:
            sort_by: Sort by 'memories', 'last_active', or 'tier'
            limit: Maximum number of users to return
            
        Returns:
            List of users with stats
        """
        users = self._get_all_users()
        
        # Sort users
        if sort_by == "memories":
            users.sort(key=lambda x: x["memory_count"], reverse=True)
        elif sort_by == "last_active":
            users.sort(key=lambda x: x.get("last_active", ""), reverse=True)
        
        # Apply limit
        if limit:
            users = users[:limit]
        
        return users
    
    def get_user_details(self, user_id: str) -> Optional[dict]:
        """
        Get detailed stats for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            User details with memories and stats
        """
        memories = self.store.get_user_memories(user_id)
        
        if not memories:
            return None
        
        # Calculate stats
        total_memories = len(memories)
        recent_memories = sorted(memories, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        
        return {
            "user_id": user_id,
            "memory_count": total_memories,
            "recent_memories": recent_memories,
            "first_memory": memories[0].get("timestamp") if memories else None,
            "last_memory": memories[-1].get("timestamp") if memories else None
        }
    
    def clear_user_data(self, user_id: str) -> dict:
        """
        Clear all data for a user
        
        Warning: This is irreversible!
        
        Args:
            user_id: User identifier
            
        Returns:
            Result with count of cleared items
        """
        cleared = self.store.clear_user_memory(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "memories_cleared": cleared,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_system_health(self) -> dict:
        """
        Get detailed system health metrics
        
        Returns:
            Health status with checks and issues
        """
        stats = self.store.get_stats()
        
        # Perform health checks
        checks = {
            "vector_sync": stats["total_vectors"] == stats["total_memories"],
            "data_present": stats["total_memories"] > 0,
            "storage_accessible": True
        }
        
        # Calculate health score
        health_score = sum(checks.values()) / len(checks) * 100
        
        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        else:
            status = "unhealthy"
        
        # Identify issues
        issues = []
        if not checks["vector_sync"]:
            issues.append({
                "severity": "warning",
                "message": "Vector count mismatch with memories",
                "action": "Run rebuild-index endpoint"
            })
        
        return {
            "status": status,
            "health_score": health_score,
            "checks": checks,
            "issues": issues,
            "metrics": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_all_users(self) -> List[dict]:
        """Get all users from memory store"""
        user_memories = {}
        
        # Group memories by user
        for memory in self.store.memory_store:
            user_id = memory.get("user_id")
            if user_id:
                if user_id not in user_memories:
                    user_memories[user_id] = []
                user_memories[user_id].append(memory)
        
        # Create user list
        users = []
        for user_id, memories in user_memories.items():
            users.append({
                "user_id": user_id,
                "memory_count": len(memories),
                "last_active": memories[-1].get("timestamp") if memories else None,
                "tier": "free"  # Would query from Supabase
            })
        
        return users
