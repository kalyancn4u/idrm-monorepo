> *Type: Document (specification) · Audience: Developers · Status: Archived — v3 historical generation*

# IDRM: Code Standards & Best Practices

<!-- IDRM-CLEANUP doc=v3-71-codestds status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — code standards → contributor guide + DoD (+ new PICS row)
> → [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md)
> + [`secure-coding-101`](../../../../guides/mvp/learn/secure-coding-101.md) + the Definition of Done
> [`../../../instructions/definition-of-done.md`](../../../instructions/definition-of-done.md). **New conformance row
> added from this doc:** `PICS-STK-QUALITY-01` (black + flake8 + mypy + type hints) in `docs/mvp/26`.
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Complete Guide for Writing Quality Code

**Version**: 3.0 Consolidated  
**Audience**: Developers & Contributors  
**Reading Time**: 50-65 minutes  
**Last Updated**: May 16, 2026

---

## 📚 **Table of Contents**

1. [Why Code Standards Matter](#1-why-code-standards-matter)
2. [General Principles](#2-general-principles)
3. [Python Code Standards](#3-python-code-standards)
4. [JavaScript Code Standards](#4-javascript-code-standards)
5. [SQL Code Standards](#5-sql-code-standards)
6. [API Design Standards](#6-api-design-standards)
7. [Testing Standards](#7-testing-standards)
8. [Documentation Standards](#8-documentation-standards)
9. [Git Commit Standards](#9-git-commit-standards)
10. [Code Review Checklist](#10-code-review-checklist)
11. [Common Patterns](#11-common-patterns)
12. [Anti-Patterns to Avoid](#12-anti-patterns-to-avoid)

---

## 1. **Why Code Standards Matter**

### 1.1 The Simple Explanation

**Code standards** are like grammar rules for programming. Just like:
- **Grammar makes writing readable** → Code standards make code readable
- **Grammar enables communication** → Code standards enable collaboration
- **Grammar shows professionalism** → Code standards show quality

### 1.2 Real-World Impact

**Without Standards (Bad Code)**:
```python
def f(x,y):
  z=x+y
  return z
```
*What does `f` do? What are `x`, `y`, `z`?*

**With Standards (Good Code)**:
```python
def calculate_total_cost(item_price: float, tax_rate: float) -> float:
    """
    Calculate the total cost including tax.
    
    Args:
        item_price: The base price of the item
        tax_rate: The tax rate as a decimal (e.g., 0.18 for 18%)
        
    Returns:
        The total cost including tax
    """
    total_cost = item_price * (1 + tax_rate)
    return total_cost
```
*Clear, documented, self-explaining!*

### 1.3 Benefits for IDRM

✅ **Consistency**: All code looks like it's written by one person  
✅ **Maintainability**: Easy to fix bugs and add features  
✅ **Collaboration**: Team members understand each other's code  
✅ **Quality**: Fewer bugs, better performance  
✅ **Onboarding**: New developers get productive faster  

---

## 2. **General Principles**

### 2.1 DRY (Don't Repeat Yourself)

**Bad** - Repetition:
```python
# Same calculation repeated 3 times
medical_total = len([s for s in services if s.service_type == 'MEDICAL'])
food_total = len([s for s in services if s.service_type == 'FOOD'])
shelter_total = len([s for s in services if s.service_type == 'SHELTER'])
```

**Good** - Reusable function:
```python
def count_by_service_type(services: List[Service], service_type: str) -> int:
    """Count services of a specific type."""
    return len([s for s in services if s.service_type == service_type])

medical_total = count_by_service_type(services, 'MEDICAL')
food_total = count_by_service_type(services, 'FOOD')
shelter_total = count_by_service_type(services, 'SHELTER')
```

---

### 2.2 KISS (Keep It Simple, Stupid)

**Bad** - Over-complicated:
```python
def is_critical(priority):
    return True if priority == 'CRITICAL' else False if priority != 'CRITICAL' else None
```

**Good** - Simple:
```python
def is_critical(priority: str) -> bool:
    """Check if priority level is critical."""
    return priority == 'CRITICAL'
```

---

### 2.3 YAGNI (You Aren't Gonna Need It)

**Bad** - Building features you don't need yet:
```python
class ServiceRequest:
    def __init__(self):
        self.service_id = uuid4()
        self.status = 'SUBMITTED'
        # Added 50 methods "just in case"...
        self.export_to_csv()
        self.export_to_excel()
        self.export_to_pdf()
        self.export_to_xml()
        self.export_to_json()
        # ...
```

**Good** - Build only what's needed now:
```python
class ServiceRequest:
    def __init__(self):
        self.service_id = uuid4()
        self.status = 'SUBMITTED'
    
    # Add export methods only when actually needed
```

---

### 2.4 Fail Fast

**Bad** - Errors discovered too late:
```python
def create_service_request(data):
    service = ServiceRequest()
    service.save()  # Save first
    service.validate()  # Validate after! ← Bug: Invalid data already saved
```

**Good** - Validate early:
```python
def create_service_request(data):
    service = ServiceRequest(data)
    service.validate()  # Validate first
    service.save()  # Save only if valid
```

---

## 3. **Python Code Standards**

### 3.1 Follow PEP 8

**PEP 8** = Python's official style guide

#### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Variables** | snake_case | `service_request`, `user_id` |
| **Functions** | snake_case | `create_service()`, `get_user()` |
| **Classes** | PascalCase | `ServiceRequest`, `UserProfile` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| **Private** | Leading underscore | `_internal_method()` |
| **Modules** | snake_case | `service_manager.py` |

**Example**:
```python
# Constants
MAX_SERVICES_PER_PAGE = 20
DEFAULT_PRIORITY = 'MEDIUM'

# Class
class ServiceRequest:
    """Represents a disaster service request."""
    
    # Class variable
    valid_statuses = ['SUBMITTED', 'APPROVED', 'COMPLETED']
    
    def __init__(self, service_type: str):
        # Instance variables
        self.service_id = uuid4()
        self.service_type = service_type
        self._is_verified = False  # Private
    
    # Public method
    def approve(self) -> bool:
        """Approve this service request."""
        return self._validate_and_approve()
    
    # Private method
    def _validate_and_approve(self) -> bool:
        """Internal validation logic."""
        # ...
```

---

### 3.2 Type Hints (Always Use Them!)

**Bad** - No type hints:
```python
def calculate_distance(point1, point2):
    # What types are point1 and point2?
    # What type is returned?
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
```

**Good** - Clear types:
```python
from typing import Tuple

def calculate_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float]
) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: First point as (x, y) coordinates
        point2: Second point as (x, y) coordinates
        
    Returns:
        Distance between points
    """
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
```

**Common Types**:
```python
from typing import List, Dict, Optional, Union, Tuple, Any
from uuid import UUID
from datetime import datetime

# Simple types
name: str = "John"
age: int = 30
price: float = 99.99
is_active: bool = True

# Collections
tags: List[str] = ["urgent", "medical"]
user_data: Dict[str, Any] = {"name": "John", "age": 30}
coordinates: Tuple[float, float] = (17.3850, 78.4867)

# Optional (can be None)
description: Optional[str] = None

# Union (one of multiple types)
status: Union[str, int] = "active"

# Complex types
service_id: UUID = uuid4()
created_at: datetime = datetime.now()
```

---

### 3.3 Docstrings (Google Style)

**Every public function/class needs a docstring!**

**Bad** - No documentation:
```python
def create_service(data):
    # What does this do? What's the format of data?
    pass
```

**Good** - Clear documentation:
```python
def create_service(data: Dict[str, Any]) -> ServiceRequest:
    """
    Create a new service request from provided data.
    
    Args:
        data: Dictionary containing service request fields:
            - service_type: Type of service (MEDICAL, FOOD, etc.)
            - priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
            - location: GeoJSON point with coordinates
            - description: Detailed description of need
            
    Returns:
        Created ServiceRequest object with generated ID
        
    Raises:
        ValidationError: If required fields are missing or invalid
        DatabaseError: If save operation fails
        
    Example:
        >>> data = {
        ...     "service_type": "MEDICAL",
        ...     "priority": "CRITICAL",
        ...     "location": {"type": "Point", "coordinates": [78.48, 17.38]},
        ...     "description": "Urgent medical attention needed"
        ... }
        >>> service = create_service(data)
        >>> print(service.service_id)
        f9e8d7c6-b5a4-3210-fedc-ba9876543210
    """
    service = ServiceRequest(**data)
    service.validate()
    service.save()
    return service
```

**Docstring Structure**:
```python
def function_name(param1: type1, param2: type2) -> return_type:
    """
    One-line summary (what does this do?).
    
    Longer description if needed. Explain the "why" not just the "what".
    This can be multiple paragraphs.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ErrorType1: When this error occurs
        ErrorType2: When this error occurs
        
    Example:
        >>> result = function_name(arg1, arg2)
        >>> print(result)
        expected output
    """
    pass
```

---

### 3.4 Error Handling

**Bad** - Generic catch-all:
```python
try:
    service = get_service(service_id)
    service.approve()
except:  # ← Never do this!
    print("Error")
```

**Good** - Specific exceptions:
```python
from fastapi import HTTPException

try:
    service = get_service(service_id)
    service.approve()
except ServiceNotFoundError:
    raise HTTPException(status_code=404, detail="Service not found")
except InsufficientPermissionsError:
    raise HTTPException(status_code=403, detail="You don't have permission to approve")
except ValidationError as e:
    raise HTTPException(status_code=400, detail=f"Validation failed: {e}")
except Exception as e:
    logger.exception("Unexpected error in service approval")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

### 3.5 Async/Await (For I/O Operations)

**Use async for**:
- Database queries
- API calls
- File I/O
- Network requests

**Example - Database Query**:
```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

async def get_service_by_id(
    db: AsyncSession,
    service_id: UUID
) -> Optional[ServiceRequest]:
    """
    Retrieve a service request by ID.
    
    Args:
        db: Database session
        service_id: UUID of the service request
        
    Returns:
        ServiceRequest if found, None otherwise
    """
    result = await db.execute(
        select(ServiceRequest).where(ServiceRequest.service_id == service_id)
    )
    return result.scalar_one_or_none()
```

**Example - API Endpoint**:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/services/{service_id}")
async def get_service(
    service_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get service request by ID."""
    service = await get_service_by_id(db, service_id)
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return service
```

---

### 3.6 Code Formatting (Black)

**Black** = Automatic Python code formatter

**Install**:
```bash
pip install black
```

**Usage**:
```bash
# Format single file
black service_manager.py

# Format entire project
black .

# Check without modifying
black --check .
```

**Example - Before Black**:
```python
def f(x,y,z):
  result=x+y+z
  return result
```

**After Black**:
```python
def f(x, y, z):
    result = x + y + z
    return result
```

**Configure in pyproject.toml**:
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''
```

---

## 4. **JavaScript Code Standards**

### 4.1 Modern JavaScript (ES6+)

#### Use `const` and `let` (Never `var`)

**Bad**:
```javascript
var userName = 'John';
var userAge = 30;
```

**Good**:
```javascript
const userName = 'John';  // Won't change
let userAge = 30;          // Might change
```

---

#### Arrow Functions

**Bad** - Old function syntax:
```javascript
function getServices(type) {
    return fetch('/api/v1/services?type=' + type);
}
```

**Good** - Arrow function:
```javascript
const getServices = (type) => {
    return fetch(`/api/v1/services?type=${type}`);
};

// Even shorter for simple returns
const getServices = (type) => fetch(`/api/v1/services?type=${type}`);
```

---

#### Template Literals

**Bad** - String concatenation:
```javascript
const message = 'Hello ' + userName + ', you have ' + count + ' notifications.';
```

**Good** - Template literals:
```javascript
const message = `Hello ${userName}, you have ${count} notifications.`;
```

---

#### Destructuring

**Bad** - Repetitive access:
```javascript
const service = response.data;
const serviceId = service.service_id;
const serviceType = service.service_type;
const priority = service.priority;
```

**Good** - Destructuring:
```javascript
const { data: service } = response;
const { service_id, service_type, priority } = service;
```

---

### 4.2 Async/Await (Not Callbacks)

**Bad** - Callback hell:
```javascript
fetchUser(userId, function(user) {
    fetchServices(user.id, function(services) {
        fetchProviders(services[0].id, function(providers) {
            displayProviders(providers);
        });
    });
});
```

**Good** - Async/await:
```javascript
async function loadUserData(userId) {
    try {
        const user = await fetchUser(userId);
        const services = await fetchServices(user.id);
        const providers = await fetchProviders(services[0].id);
        displayProviders(providers);
    } catch (error) {
        console.error('Error loading user data:', error);
        showError(error.message);
    }
}
```

---

### 4.3 Error Handling

**Always use try-catch with async/await**:

```javascript
async function createService(serviceData) {
    try {
        const response = await fetch('/api/v1/services', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAccessToken()}`
            },
            body: JSON.stringify(serviceData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.data;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Failed to create service:', error);
        throw error;  // Re-throw for caller to handle
    }
}

// Usage
try {
    const service = await createService(formData);
    showSuccess(`Service ${service.service_id} created!`);
    redirectToDashboard();
} catch (error) {
    showError(`Failed to create service: ${error.message}`);
}
```

---

### 4.4 Naming Conventions

**Variables and Functions**: camelCase
```javascript
const serviceRequest = { ... };
const userName = 'John';

function getUserById(userId) { ... }
async function fetchServices() { ... }
```

**Classes**: PascalCase
```javascript
class ServiceManager {
    constructor() {
        this.services = [];
    }
    
    addService(service) {
        this.services.push(service);
    }
}
```

**Constants**: UPPER_SNAKE_CASE
```javascript
const MAX_RETRY_ATTEMPTS = 3;
const API_BASE_URL = 'https://api.idrm.gov.in';
const DEFAULT_TIMEOUT = 5000;
```

---

### 4.5 JSDoc Comments

**Document all public functions**:

```javascript
/**
 * Fetch services filtered by type and priority.
 * 
 * @param {string} serviceType - Type of service (MEDICAL, FOOD, etc.)
 * @param {string} priority - Priority level (CRITICAL, HIGH, MEDIUM, LOW)
 * @param {number} [limit=20] - Maximum number of results (optional)
 * @returns {Promise<Array<Service>>} Array of service objects
 * @throws {Error} If API request fails
 * 
 * @example
 * const services = await getServices('MEDICAL', 'CRITICAL');
 * console.log(`Found ${services.length} critical medical services`);
 */
async function getServices(serviceType, priority, limit = 20) {
    const params = new URLSearchParams({
        service_type: serviceType,
        priority: priority,
        limit: limit.toString()
    });
    
    const response = await fetch(`/api/v1/services?${params}`);
    const data = await response.json();
    
    if (data.status !== 'success') {
        throw new Error(data.message);
    }
    
    return data.data.services;
}
```

---

## 5. **SQL Code Standards**

### 5.1 Formatting

**Keywords**: UPPERCASE  
**Identifiers**: snake_case  
**Indentation**: 2 or 4 spaces

**Example**:
```sql
-- Good SQL formatting
SELECT 
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    ST_AsGeoJSON(s.location) AS location_geojson,
    u.full_name AS requestor_name,
    o.name AS provider_organization
FROM service_requests s
INNER JOIN users u ON s.requestor_id = u.user_id
LEFT JOIN users p ON s.assigned_to = p.user_id
LEFT JOIN organizations o ON p.organization_id = o.org_id
WHERE s.status IN ('APPROVED', 'IN_PROGRESS', 'COMPLETED')
    AND s.priority IN ('CRITICAL', 'HIGH')
    AND s.created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY 
    s.priority DESC,
    s.created_at ASC
LIMIT 100;
```

---

### 5.2 Always Use Prepared Statements

**Bad** - SQL injection vulnerability:
```python
# NEVER DO THIS!
service_type = request.query_params.get('type')
query = f"SELECT * FROM service_requests WHERE service_type = '{service_type}'"
result = db.execute(query)
```
*An attacker could send: `type=MEDICAL'; DROP TABLE service_requests; --`*

**Good** - Parameterized query:
```python
from sqlalchemy import select

service_type = request.query_params.get('type')
query = select(ServiceRequest).where(ServiceRequest.service_type == service_type)
result = await db.execute(query)
```

---

### 5.3 Use Meaningful Aliases

**Bad** - Cryptic aliases:
```sql
SELECT 
    s.st AS x,
    s.pr AS y,
    u.fn AS z
FROM service_requests s
JOIN users u ON s.rid = u.uid
```

**Good** - Descriptive aliases:
```sql
SELECT 
    s.service_type,
    s.priority,
    u.full_name AS requestor_name
FROM service_requests s
JOIN users u ON s.requestor_id = u.user_id
```

---

### 5.4 Comment Complex Queries

```sql
-- Find all CRITICAL services that have been waiting more than 30 minutes
-- without being assigned to a provider. This query is used by the
-- alert system to notify coordinators of delayed responses.
WITH pending_critical AS (
    SELECT 
        service_id,
        service_type,
        created_at,
        EXTRACT(EPOCH FROM (NOW() - created_at)) / 60 AS minutes_waiting
    FROM service_requests
    WHERE priority = 'CRITICAL'
        AND status = 'APPROVED'
        AND assigned_to IS NULL
)
SELECT *
FROM pending_critical
WHERE minutes_waiting > 30
ORDER BY minutes_waiting DESC;
```

---

## 6. **API Design Standards**

### 6.1 RESTful URL Structure

**Pattern**: `/api/v{version}/{resource}`

**Examples**:
```
GET    /api/v1/services           ← List all services
POST   /api/v1/services           ← Create new service
GET    /api/v1/services/{id}      ← Get specific service
PUT    /api/v1/services/{id}      ← Update service
DELETE /api/v1/services/{id}      ← Delete service

GET    /api/v1/users              ← List users
GET    /api/v1/users/{id}         ← Get user
GET    /api/v1/users/{id}/services ← Get user's services

GET    /api/v1/organizations      ← List organizations
POST   /api/v1/organizations/{id}/verify ← Verify organization
```

---

### 6.2 HTTP Methods

| Method | Purpose | Safe? | Idempotent? | Body? |
|--------|---------|-------|-------------|-------|
| **GET** | Retrieve data | ✅ Yes | ✅ Yes | ❌ No |
| **POST** | Create new resource | ❌ No | ❌ No | ✅ Yes |
| **PUT** | Update/replace resource | ❌ No | ✅ Yes | ✅ Yes |
| **PATCH** | Partial update | ❌ No | ❌ No | ✅ Yes |
| **DELETE** | Remove resource | ❌ No | ✅ Yes | ❌ Usually no |

---

### 6.3 Status Codes

**Use appropriate HTTP status codes**:

```python
from fastapi import HTTPException, status

# 200 OK - Success (GET, PUT, PATCH)
return {"status": "success", "data": service}

# 201 Created - Resource created (POST)
return JSONResponse(
    status_code=status.HTTP_201_CREATED,
    content={"status": "success", "data": service}
)

# 204 No Content - Success with no body (DELETE)
return Response(status_code=status.HTTP_204_NO_CONTENT)

# 400 Bad Request - Validation error
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid service type"
)

# 401 Unauthorized - Not authenticated
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required"
)

# 403 Forbidden - Authenticated but not authorized
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You don't have permission to approve services"
)

# 404 Not Found - Resource doesn't exist
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Service {service_id} not found"
)

# 500 Internal Server Error - Unexpected error
raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="An internal error occurred"
)
```

---

## 7. **Testing Standards**

### 7.1 Test Coverage Targets

| Component | Target Coverage | Why? |
|-----------|----------------|------|
| **Critical paths** (auth, payments) | 95%+ | Lives depend on it |
| **Business logic** | 80%+ | Core functionality |
| **API endpoints** | 75%+ | Integration points |
| **Utilities** | 70%+ | Reusable code |
| **Overall** | 70%+ | Industry standard |

---

### 7.2 Unit Tests (Python/pytest)

**Test file naming**: `test_*.py` or `*_test.py`

**Example**:
```python
import pytest
from app.services.service_manager import ServiceManager
from app.models import ServiceRequest

@pytest.mark.asyncio
async def test_create_service_success(db_session):
    """Test successful service request creation."""
    # Arrange
    service_data = {
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "location": {"type": "Point", "coordinates": [78.48, 17.38]},
        "address": "Charminar, Hyderabad",
        "description": "Urgent medical attention needed"
    }
    
    # Act
    service = await ServiceManager.create_service(db_session, service_data)
    
    # Assert
    assert service.service_id is not None
    assert service.service_type == "MEDICAL"
    assert service.priority == "CRITICAL"
    assert service.status == "SUBMITTED"

@pytest.mark.asyncio
async def test_create_service_invalid_type(db_session):
    """Test service creation with invalid service type."""
    service_data = {
        "service_type": "INVALID",  # ← Invalid enum value
        "priority": "CRITICAL",
        "location": {"type": "Point", "coordinates": [78.48, 17.38]},
        "description": "Test"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        await ServiceManager.create_service(db_session, service_data)
    
    assert "Invalid service type" in str(exc_info.value)
```

---

### 7.3 Integration Tests

**Test entire API endpoints**:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_service_workflow(client: AsyncClient):
    """Test complete service request workflow."""
    
    # 1. Register user
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "phone": "9876543210",
            "role": "CITIZEN"
        }
    )
    assert register_response.status_code == 201
    
    # 2. Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["data"]["access_token"]
    
    # 3. Create service request
    create_response = await client.post(
        "/api/v1/services",
        json={
            "service_type": "MEDICAL",
            "priority": "CRITICAL",
            "location": {"type": "Point", "coordinates": [78.48, 17.38]},
            "address": "Test Address",
            "description": "Test service"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert create_response.status_code == 201
    service_id = create_response.json()["data"]["service_id"]
    
    # 4. Fetch created service
    get_response = await client.get(
        f"/api/v1/services/{service_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert get_response.status_code == 200
    assert get_response.json()["data"]["service_type"] == "MEDICAL"
```

---

### 7.4 Test Organization

**Structure**:
```
tests/
├── unit/
│   ├── test_service_manager.py
│   ├── test_user_service.py
│   └── test_geospatial.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_service_api.py
│   └── test_admin_api.py
├── e2e/
│   ├── test_service_workflow.py
│   └── test_user_journey.py
└── conftest.py  ← Shared fixtures
```

**conftest.py example**:
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.database import Base

@pytest.fixture
async def db_session():
    """Create a test database session."""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()
```

---

## 8. **Documentation Standards**

### 8.1 README Files

**Every component needs a README.md**:

```markdown
# Service Manager

Handles service request CRUD operations and matching logic.

## Purpose

- Create, read, update, delete service requests
- Match requests with suitable providers
- Track service status transitions
- Generate service analytics

## Usage

```python
from app.services.service_manager import ServiceManager

# Create service
service = await ServiceManager.create_service(db, service_data)

# Find nearby services
nearby = await ServiceManager.find_nearby(db, location, radius=5000)
```

## Dependencies

- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostGIS 3.4+

## Configuration

Set these environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MAX_SERVICE_RADIUS`: Maximum search radius (meters)

## Testing

```bash
pytest tests/unit/test_service_manager.py -v
```

## Related Documentation

- [API Specification](../docs/api-spec.md)
- [Database Schema](../docs/schema.md)
```

---

### 8.2 Inline Code Comments

**When to comment**:
- ✅ Complex algorithms
- ✅ Business logic that's not obvious
- ✅ Workarounds for bugs
- ✅ Performance optimizations
- ✅ Security considerations

**When NOT to comment**:
- ❌ Obvious code
- ❌ Repeating what code already says

**Bad comments**:
```python
# Set user to John
user = "John"

# Add 1 to counter
counter += 1

# Loop through services
for service in services:
    # Print service
    print(service)
```

**Good comments**:
```python
# Use haversine formula for more accurate distance calculation
# on spherical earth. Standard Euclidean distance would be
# inaccurate for geographic coordinates.
distance = haversine_distance(point1, point2)

# WORKAROUND: PostGIS ST_DWithin has a bug with SRID 4326
# at the poles. We convert to meters first.
# See: https://trac.osgeo.org/postgis/ticket/5432
geometry = ST_Transform(location, 3857)

# Performance: Use connection pool to avoid creating
# new connections for every request. Reduces latency
# by ~200ms per request.
db = await get_pooled_connection()
```

---

## 9. **Git Commit Standards**

### 9.1 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring (no behavior change)
- `test`: Adding or updating tests
- `chore`: Maintenance (dependencies, config)

**Examples**:

```
feat(services): Add geospatial clustering endpoint

Implement K-means clustering algorithm for grouping
nearby service requests. Reduces map marker clutter
when displaying 100+ requests.

Closes #142
```

```
fix(auth): Prevent token refresh race condition

Multiple simultaneous API calls were causing duplicate
token refresh requests. Added mutex lock to ensure
only one refresh happens at a time.

Fixes #289
```

```
docs(api): Update service request schema examples

Added examples for all service types (MEDICAL, FOOD,
SHELTER, etc.) with realistic data.
```

---

### 9.2 Commit Best Practices

**✅ DO**:
- Write in present tense ("Add feature" not "Added feature")
- Keep subject line under 50 characters
- Capitalize subject line
- Don't end subject with period
- Use body to explain "why" not "what"
- Reference issues/PRs in footer

**❌ DON'T**:
- Commit commented-out code
- Commit merge commits to feature branches
- Commit credentials or secrets
- Make huge commits (split into smaller)
- Use vague messages like "fix stuff" or "WIP"

---

## 10. **Code Review Checklist**

### 10.1 Functionality

- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error cases are handled
- [ ] No obvious bugs

### 10.2 Code Quality

- [ ] Follows code standards (PEP 8, ES6)
- [ ] No code duplication (DRY principle)
- [ ] Functions are small and focused
- [ ] Names are clear and descriptive
- [ ] No magic numbers (use constants)

### 10.3 Testing

- [ ] Unit tests included
- [ ] Integration tests if needed
- [ ] Tests actually test what they claim to test
- [ ] Tests pass locally
- [ ] Coverage doesn't decrease

### 10.4 Documentation

- [ ] Docstrings on public functions
- [ ] README updated if needed
- [ ] API docs updated if needed
- [ ] Comments explain "why" not "what"

### 10.5 Security

- [ ] No SQL injection vulnerabilities
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Authentication/authorization checked
- [ ] Sensitive data not logged

### 10.6 Performance

- [ ] No obvious performance issues
- [ ] Database queries optimized
- [ ] No N+1 query problems
- [ ] Proper indexing used

---

## 11. **Common Patterns**

### 11.1 Repository Pattern (Data Access)

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ServiceRepository:
    """Repository for service request data access."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, service_id: UUID) -> Optional[ServiceRequest]:
        """Get service by ID."""
        result = await self.db.execute(
            select(ServiceRequest).where(ServiceRequest.service_id == service_id)
        )
        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        service_type: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 20
    ) -> List[ServiceRequest]:
        """List services with optional filters."""
        query = select(ServiceRequest)
        
        if service_type:
            query = query.where(ServiceRequest.service_type == service_type)
        if priority:
            query = query.where(ServiceRequest.priority == priority)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, service_data: dict) -> ServiceRequest:
        """Create new service."""
        service = ServiceRequest(**service_data)
        self.db.add(service)
        await self.db.commit()
        await self.db.refresh(service)
        return service
    
    async def update(self, service: ServiceRequest) -> ServiceRequest:
        """Update existing service."""
        await self.db.commit()
        await self.db.refresh(service)
        return service
    
    async def delete(self, service: ServiceRequest) -> None:
        """Delete service."""
        await self.db.delete(service)
        await self.db.commit()
```

---

### 11.2 Service Layer Pattern (Business Logic)

```python
class ServiceManager:
    """Business logic for service management."""
    
    def __init__(self, repo: ServiceRepository):
        self.repo = repo
    
    async def create_service(self, service_data: dict) -> ServiceRequest:
        """
        Create service with validation and business logic.
        """
        # Validate
        self._validate_service_data(service_data)
        
        # Create
        service = await self.repo.create(service_data)
        
        # Business logic: Auto-approve based on criteria
        if self._should_auto_approve(service):
            service.status = 'APPROVED'
            service = await self.repo.update(service)
            
            # Trigger provider matching
            await self._match_providers(service)
        
        return service
    
    def _validate_service_data(self, data: dict) -> None:
        """Validate service data."""
        if data.get('service_type') not in VALID_SERVICE_TYPES:
            raise ValidationError("Invalid service type")
        
        # More validation...
    
    def _should_auto_approve(self, service: ServiceRequest) -> bool:
        """Determine if service should be auto-approved."""
        # Business rule: Critical priority auto-approved
        return service.priority == 'CRITICAL'
    
    async def _match_providers(self, service: ServiceRequest) -> None:
        """Find and notify suitable providers."""
        # Matching logic...
        pass
```

---

## 12. **Anti-Patterns to Avoid**

### 12.1 God Object

**Bad** - One class does everything:
```python
class ServiceManager:
    def create_service(self): pass
    def update_service(self): pass
    def delete_service(self): pass
    def approve_service(self): pass
    def assign_provider(self): pass
    def send_notification(self): pass
    def calculate_distance(self): pass
    def generate_report(self): pass
    def export_to_csv(self): pass
    # ... 50 more methods ...
```

**Good** - Separated concerns:
```python
class ServiceRepository:
    """Data access only."""
    pass

class ServiceApprovalService:
    """Approval logic only."""
    pass

class ProviderMatchingService:
    """Matching logic only."""
    pass

class NotificationService:
    """Notifications only."""
    pass
```

---

### 12.2 Hardcoded Values

**Bad**:
```python
def check_critical_services():
    services = db.query("SELECT * FROM services WHERE priority = 'CRITICAL'")
    if len(services) > 10:  # ← Magic number!
        send_alert("admin@example.com")  # ← Hardcoded email!
```

**Good**:
```python
from config import CRITICAL_SERVICE_THRESHOLD, ADMIN_EMAIL

def check_critical_services():
    services = db.query("SELECT * FROM services WHERE priority = 'CRITICAL'")
    if len(services) > CRITICAL_SERVICE_THRESHOLD:
        send_alert(ADMIN_EMAIL)
```

---

### 12.3 Premature Optimization

**Bad** - Optimizing before measuring:
```python
# Spent 3 days writing complex caching logic
# for a function called once per hour!
@lru_cache(maxsize=1000)
@redis_cache(ttl=3600)
@memory_cache(size=500)
def calculate_monthly_stats():
    # Called once per hour
    pass
```

**Good** - Optimize what matters:
```python
# Measure first
profiling_data = profile_application()

# Optimize the slow parts
# (This function is called 10,000 times/second)
@redis_cache(ttl=300)
def get_nearby_services(location):
    # This IS worth caching!
    pass
```

---

## 🎉 **You're Ready to Write Quality Code!**

You now understand:

✅ **Why standards matter** (consistency, maintainability, collaboration)  
✅ **Python standards** (PEP 8, type hints, docstrings, async/await)  
✅ **JavaScript standards** (ES6+, async/await, error handling)  
✅ **SQL standards** (formatting, prepared statements, comments)  
✅ **API design** (RESTful URLs, HTTP methods, status codes)  
✅ **Testing standards** (coverage targets, unit tests, integration tests)  
✅ **Documentation** (READMEs, inline comments, docstrings)  
✅ **Git commits** (format, best practices, meaningful messages)  
✅ **Code review** (what to check, how to improve)  
✅ **Common patterns** (repository, service layer)  
✅ **Anti-patterns** (what to avoid)  

---

## 📚 **What's Next?**

- **[42-VERIFICATION-CHECKLISTS.md](42-VERIFICATION-CHECKLISTS.md)** - Testing and quality assurance
- **[40-DATA-FORMATS.md](40-DATA-FORMATS.md)** - JSON and API data structures
- **[43-CONTRIBUTION-GUIDE.md](43-CONTRIBUTION-GUIDE.md)** - How to contribute to IDRM

---

**Document Information**  
**Created**: May 16, 2026  
**Purpose**: Complete guide to IDRM code standards  
**Difficulty**: 🟡 Intermediate (beginner-friendly explanations)  
**Estimated Reading Time**: 50-65 minutes  
**Part of**: IDRM Documentation Series (Document 41/43)
