---
inclusion: always
---

# Code Style Guidelines for Memory Layer

## General Principles
- Write clean, readable code that other developers can understand
- Prefer explicit over implicit
- Use meaningful variable and function names
- Keep functions small and focused on a single responsibility
- Comment complex logic, not obvious code

## JavaScript/TypeScript (Extension & Web App)

### Naming Conventions
- **Variables/Functions**: camelCase (`getUserMemories`, `memoryCount`)
- **Components**: PascalCase (`MemoryCard`, `SearchBar`)
- **Constants**: UPPER_SNAKE_CASE (`API_BASE_URL`, `MAX_RETRIES`)
- **Files**: kebab-case (`memory-card.tsx`, `use-memories.ts`)

### Code Structure
```typescript
// Imports grouped by: external, internal, types
import { useState } from 'react';
import { fetchMemories } from '@/lib/api';
import type { Memory } from '@/types';

// Type definitions before implementation
interface Props {
  userId: string;
}

// Component or function
export function MemoryList({ userId }: Props) {
  // Hooks first
  const [memories, setMemories] = useState<Memory[]>([]);
  
  // Event handlers
  const handleRefresh = async () => {
    // Implementation
  };
  
  // Render
  return (
    // JSX
  );
}
```

### Best Practices
- Use async/await instead of .then() chains
- Destructure props and state for cleaner code
- Use optional chaining (?.) and nullish coalescing (??)
- Prefer const over let, never use var
- Use template literals for string interpolation

## Python (Backend)

### Naming Conventions
- **Variables/Functions**: snake_case (`get_user_memories`, `memory_count`)
- **Classes**: PascalCase (`MemoryService`, `UserRepository`)
- **Constants**: UPPER_SNAKE_CASE (`API_VERSION`, `MAX_MEMORIES_PER_PAGE`)
- **Files**: snake_case (`memory_service.py`, `user_repository.py`)

### Code Structure
```python
# Imports grouped by: standard library, third-party, local
from datetime import datetime
from fastapi import APIRouter, Depends
from .models import Memory
from .services import MemoryService

# Type hints always
async def get_memories(
    user_id: str,
    limit: int = 10,
    service: MemoryService = Depends()
) -> list[Memory]:
    """Fetch user memories with pagination.
    
    Args:
        user_id: The user's unique identifier
        limit: Maximum number of memories to return
        service: Injected memory service
        
    Returns:
        List of Memory objects
    """
    return await service.get_user_memories(user_id, limit)
```

### Best Practices
- Always use type hints
- Write docstrings for public functions (Google style)
- Use async/await for I/O operations
- Prefer Pydantic models for data validation
- Use context managers (with) for resources

## Error Handling

### Frontend
```typescript
try {
  const data = await fetchMemories();
  setMemories(data);
} catch (error) {
  console.error('Failed to fetch memories:', error);
  toast.error('Could not load memories. Please try again.');
}
```

### Backend
```python
from fastapi import HTTPException

async def get_memory(memory_id: str) -> Memory:
    memory = await db.get(memory_id)
    if not memory:
        raise HTTPException(
            status_code=404,
            detail=f"Memory {memory_id} not found"
        )
    return memory
```

## Testing
- Write tests for critical business logic
- Use descriptive test names: `test_should_return_404_when_memory_not_found`
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies

## Security
- Never commit secrets or API keys
- Validate all user input
- Use parameterized queries (no string concatenation)
- Implement proper CORS policies
- Always verify authentication tokens

## Performance
- Minimize database queries (use joins, batch operations)
- Implement pagination for large datasets
- Use caching for frequently accessed data
- Lazy load images and heavy components
- Debounce user input for search

---

*These guidelines ensure consistency across the Memory Layer codebase.*
