> *Type: Document (specification) · Audience: Backend developers · Status: Archived — v3 historical generation*

# IDRM: Complete Backend Implementation Guide  

<!-- IDRM-CLEANUP doc=v3-31-backend status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — backend design → `docs/mvp/30`
> Gen-3 backend implementation. Current source of truth = [`../../../../docs/mvp/30-design-data-flow-and-modules.md`](../../../../docs/mvp/30-design-data-flow-and-modules.md)
> (module skeleton router→schemas→service→repository→models) + `docs/mvp/20`; module elucidation `docs/mvp/25`;
> conformance `docs/mvp/26` (`PICS-STK-REPO-01`, `PICS-STK-VALID-01`). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Building Python FastAPI Microservices from Scratch (For Complete Novices!)

**Version**: 3.0 Consolidated  
**Audience**: Complete beginners, junior developers, anyone new to backend development  
**Technology**: Python 3.11 + FastAPI + PostgreSQL + SQLAlchemy  
**Reading Time**: 4-5 hours (implement step-by-step!)  
**Last Updated**: May 15, 2026

---

## 📚 **Table of Contents**

1. [What Is a Backend?](#1-what-is-a-backend)
2. [Technology Stack Overview](#2-technology-stack-overview)  
3. [Prerequisites & Setup](#3-prerequisites--setup)
4. [Project Structure](#4-project-structure)
5. [Database Models (SQLAlchemy)](#5-database-models-sqlalchemy)
6. [API Schemas (Pydantic)](#6-api-schemas-pydantic)
7. [CRUD Operations](#7-crud-operations)
8. [Authentication & JWT](#8-authentication--jwt)
9. [API Endpoints (FastAPI)](#9-api-endpoints-fastapi)
10. [Geospatial Queries](#10-geospatial-queries)
11. [Testing](#11-testing)
12. [Deployment](#12-deployment)

---

## 1. **What Is a Backend?**

### 1.1 Simple Explanation (For Complete Novices)

**Backend** = The server-side application that users DON'T see

**Restaurant analogy** (continued from frontend):
- **Frontend** = Dining room (what customers see)
- **Backend** = Kitchen (where food is prepared)  
- **Database** = Pantry/refrigerator (where ingredients are stored)

**In IDRM**:
```
User clicks "Create Service Request" button (Frontend)
   ↓
Frontend sends HTTP POST request to backend
   ↓
Backend receives request → Validates data → Saves to database
   ↓
Backend sends response back to frontend
   ↓
Frontend shows "Request created successfully!"
```

### 1.2 What You'll Build

**8 Python FastAPI microservices**:
1. **Auth Service** (Port 8001) - User authentication, JWT tokens
2. **Service Management** (Port 8002) - CRUD for service requests
3. **Provider Management** (Port 8003) - Service providers
4. **Geospatial Service** (Port 8004) - Map queries, spatial operations
5. **Notifications** (Port 8005) - Email/SMS alerts
6. **Search** (Port 8006) - Full-text search
7. **Admin** (Port 8007) - System administration
8. **Chatbot** (Port 8008) - AI assistance (future)

**For MVP, focus on**: Auth + Service Management + Geospatial (services 1-4)

---

## 2. **Technology Stack Overview**

### 2.1 Why Python?

**Python advantages**:
- ✅ Easy to learn and read
- ✅ Excellent geospatial libraries (Shapely, GeoPandas)
- ✅ Great for data processing
- ✅ Huge community and ecosystem
- ✅ Perfect for scientific computing

### 2.2 Why FastAPI?

**FastAPI** = Modern Python web framework

**Alternatives comparison**:

| Framework | Speed | Type Safety | Auto Docs | Learning Curve |
|-----------|-------|-------------|-----------|----------------|
| **FastAPI** | ⚡ Very Fast | ✅ Yes | ✅ Yes | 🟢 Easy |
| Django | 🐢 Slow | ❌ No | ❌ No | 🔴 Hard |
| Flask | 🏃 Medium | ❌ No | ❌ No | 🟢 Easy |

**Why FastAPI wins**:
- ✅ **Fast** - As fast as Node.js/Go
- ✅ **Type hints** - Catches errors early
- ✅ **Auto docs** - Swagger UI built-in
- ✅ **Async/await** - Modern Python
- ✅ **Pydantic** - Automatic validation

### 2.3 Stack Components

**Python 3.11** - Language  
**FastAPI** - Web framework  
**SQLAlchemy** - Database ORM (Object-Relational Mapping)  
**Pydantic** - Data validation  
**PostgreSQL** - Database  
**PostGIS** - Geospatial extension  
**Uvicorn** - ASGI server (runs FastAPI)

---

## 3. **Prerequisites & Setup**

### 3.1 What You Need

**Software**:
1. ✅ Python 3.11 (via Miniconda)
2. ✅ PostgreSQL 16 + PostGIS 3.4
3. ✅ VS Code or any code editor
4. ✅ Postman or Thunder Client (for API testing)

**Knowledge**:
- ✅ Basic Python (variables, functions, classes)
- ✅ Basic SQL (SELECT, INSERT, UPDATE, DELETE)
- ❌ No FastAPI experience needed (we'll teach you!)

### 3.2 Environment Setup (30 minutes)

#### **Step 1: Install Miniconda** (if not already installed)

```bash
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install
bash Miniconda3-latest-Linux-x86_64.sh

# Restart terminal
source ~/.bashrc
```

#### **Step 2: Create Python Environment**

```bash
# Create environment with Python 3.11
conda create -n idrm-backend python=3.11 -y

# Activate environment
conda activate idrm-backend

# You should see (idrm-backend) in your prompt
```

#### **Step 3: Install Dependencies**

```bash
# Install FastAPI and web server
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"

# Install database libraries
pip install sqlalchemy==2.0.23
pip install asyncpg==0.29.0        # PostgreSQL async driver
pip install geoalchemy2==0.14.2    # PostGIS support

# Install authentication & security
pip install python-jose[cryptography]==3.3.0  # JWT tokens
pip install passlib[bcrypt]==1.7.4             # Password hashing

# Install validation & utilities
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install python-dotenv==1.0.0

# Install geospatial libraries
pip install shapely==2.0.2
pip install geojson==3.0.1

# Install testing
pip install pytest==7.4.3
pip install httpx==0.25.2  # For testing async endpoints
```

#### **Step 4: Verify Installation**

```bash
# Check Python version
python --version  # Should show Python 3.11.x

# Check FastAPI
python -c "import fastapi; print(fastapi.__version__)"  # Should show 0.104.1

# Check SQLAlchemy
python -c "import sqlalchemy; print(sqlalchemy.__version__)"  # Should show 2.0.23
```

---

## 4. **Project Structure**

### 4.1 Create Project Folder Structure

```bash
mkdir -p idrm-backend
cd idrm-backend

# Create directory structure
mkdir -p app/{api/v1,core,db,models,schemas,services,utils}
mkdir -p tests
mkdir -p alembic/versions

# Create __init__.py files (makes folders Python packages)
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/core/__init__.py
touch app/db/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
```

**Final structure**:
```
idrm-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── services.py     # Service request endpoints
│   │       ├── providers.py    # Provider endpoints
│   │       └── geo.py          # Geospatial endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   └── security.py        # JWT & password hashing
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py         # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # User model (SQLAlchemy)
│   │   ├── service_request.py # Service request model
│   │   └── provider.py        # Provider model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # User schemas (Pydantic)
│   │   ├── service_request.py # Service schemas
│   │   └── token.py           # JWT token schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py    # User business logic
│   │   └── service_crud.py    # Service CRUD operations
│   └── utils/
│       ├── __init__.py
│       └── helpers.py         # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_services.py
├── alembic/                    # Database migrations
│   └── versions/
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 5. **Database Models (SQLAlchemy)**

### 5.1 What Is SQLAlchemy?

**SQLAlchemy** = Python library that lets you work with databases using Python objects instead of SQL

**Without SQLAlchemy** (raw SQL):
```python
# Manually write SQL queries
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
result = cursor.fetchone()
```

**With SQLAlchemy** (Pythonic):
```python
# Use Python objects
user = db.query(User).filter(User.email == email).first()
```

**Benefits**:
- ✅ Write Python, not SQL
- ✅ Type safety
- ✅ Automatic migrations
- ✅ Works with any SQL database

### 5.2 Database Configuration

**Create**: `app/core/config.py`

```python
"""
Application configuration
Loads settings from environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "IDRM Backend"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://idrm_user:idrm_password@localhost:5432/idrm_db"
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7      # 7 days
    
    # CORS (allowed origins)
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()
```

**Create**: `.env` (environment variables file)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://idrm_user:idrm_password@localhost:5432/idrm_db

# Security (IMPORTANT: Change in production!)
JWT_SECRET_KEY=super-secret-key-replace-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256

# Application
PROJECT_NAME=IDRM Backend
DEBUG=True
```

### 5.3 Database Session

**Create**: `app/db/session.py`

```python
"""
Database session management
Handles connections to PostgreSQL
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL queries (set False in production)
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for all models
Base = declarative_base()

# Dependency for FastAPI
async def get_db():
    """
    Dependency that provides database session to endpoints
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 5.4 User Model

**Create**: `app/models/user.py`

```python
"""
User model
Represents users table in database
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.db.session import Base

class UserRole(str, enum.Enum):
    """User role enumeration"""
    CITIZEN = "CITIZEN"
    SERVICE_PROVIDER = "SERVICE_PROVIDER"
    AUTHORITY = "AUTHORITY"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    # Primary key
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile fields
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Role and status
    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.CITIZEN
    )
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.email}>"
```

**What each field means**:
- `user_id` - Unique identifier (UUID)
- `email` - User's email (unique, indexed for fast lookups)
- `password_hash` - Hashed password (NEVER store plain passwords!)
- `full_name` - User's display name
- `role` - What the user can do (CITIZEN, PROVIDER, etc.)
- `is_active` - Can user log in? (True/False)
- `is_verified` - Has email been verified?
- `created_at` - When user registered
- `updated_at` - Last profile update

### 5.5 Service Request Model

**Create**: `app/models/service_request.py`

```python
"""
Service Request model
Represents service_requests table with geospatial data
"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import uuid
import enum
from app.db.session import Base

class ServiceType(str, enum.Enum):
    """Types of services"""
    MEDICAL = "MEDICAL"
    FOOD = "FOOD"
    SHELTER = "SHELTER"
    RESCUE = "RESCUE"
    WATER = "WATER"
    SANITATION = "SANITATION"
    TRANSPORT = "TRANSPORT"

class PriorityLevel(str, enum.Enum):
    """Priority levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ServiceStatus(str, enum.Enum):
    """Service request status"""
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class ServiceRequest(Base):
    """Service request database model"""
    __tablename__ = "service_requests"
    
    # Primary key
    request_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Service details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False, index=True)
    priority = Column(SQLEnum(PriorityLevel), nullable=False, index=True)
    status = Column(
        SQLEnum(ServiceStatus),
        nullable=False,
        default=ServiceStatus.SUBMITTED,
        index=True
    )
    
    # Geospatial data (PostGIS)
    location = Column(
        Geometry('POINT', srid=4326),  # WGS84 coordinate system
        nullable=False,
        index=True  # Spatial index for fast queries
    )
    location_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    
    # Relationships (foreign keys)
    requestor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ServiceRequest {self.title} ({self.status})>"
```

**Geospatial field explained**:
```python
location = Column(Geometry('POINT', srid=4326), ...)

# 'POINT' = GPS coordinate (latitude, longitude)
# srid=4326 = WGS84 coordinate system (standard GPS)
# Example: POINT(78.4867 17.385) = Hyderabad, India
```

---

## 6. **API Schemas (Pydantic)**

### 6.1 What Is Pydantic?

**Pydantic** = Data validation library

**Purpose**: Ensure data is correct before saving to database

**Example**:
```python
# Without Pydantic
email = request.json.get('email')  # Might be None, invalid format, etc.

# With Pydantic
class UserCreate(BaseModel):
    email: EmailStr  # Automatically validates email format!
    password: str
```

### 6.2 User Schemas

**Create**: `app/schemas/user.py`

```python
"""
User Pydantic schemas
Used for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# Base schema (shared fields)
class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)

# Request schema (creating user)
class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

# Update schema
class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)

# Response schema (what API returns)
class UserResponse(UserBase):
    """Schema for user in API responses"""
    user_id: UUID
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows loading from SQLAlchemy models

# Login schema
class UserLogin(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str
```

**Why separate schemas?**:
- `UserCreate` - Creating new user (includes password)
- `UserResponse` - Returning user data (NO password!)
- `UserUpdate` - Updating profile (all fields optional)

### 6.3 Service Request Schemas

**Create**: `app/schemas/service_request.py`

```python
"""
Service Request Pydantic schemas
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class ServiceRequestBase(BaseModel):
    """Base service request fields"""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    service_type: str
    priority: str
    location_name: str = Field(..., max_length=255)
    address: Optional[str] = None

class ServiceRequestCreate(ServiceRequestBase):
    """Schema for creating service request"""
    latitude: float = Field(..., ge=-90, le=90)   # -90 to 90
    longitude: float = Field(..., ge=-180, le=180)  # -180 to 180

class ServiceRequestUpdate(BaseModel):
    """Schema for updating service request"""
    status: Optional[str] = None
    provider_id: Optional[UUID] = None

class ServiceRequestResponse(ServiceRequestBase):
    """Schema for service request in API responses"""
    request_id: UUID
    status: str
    requestor_id: UUID
    provider_id: Optional[UUID]
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 6.4 Token Schemas

**Create**: `app/schemas/token.py`

```python
"""
JWT Token schemas
"""
from pydantic import BaseModel

class Token(BaseModel):
    """Response with access and refresh tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data stored in JWT token"""
    user_id: str
    email: str
    role: str
```

---

## 7. **CRUD Operations**

### 7.1 What Is CRUD?

**CRUD** = Create, Read, Update, Delete (basic database operations)

**Example**:
- **Create** - Add new user
- **Read** - Get user by ID or email
- **Update** - Change user's name
- **Delete** - Remove user account

### 7.2 User Service (Business Logic)

**Create**: `app/services/user_service.py`

```python
"""
User service - Business logic for user operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserService:
    """User business logic"""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create new user
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing = await UserService.get_by_email(db, user_data.email)
        if existing:
            raise ValueError("Email already registered")
        
        # Create user object
        db_user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone
        )
        
        # Add to database
        db.add(db_user)
        await db.flush()  # Flush to get user_id
        await db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Returns:
            User if authentication successful, None otherwise
        """
        user = await UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user profile"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None
        
        # Update fields if provided
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.phone is not None:
            user.phone = user_data.phone
        
        await db.flush()
        await db.refresh(user)
        return user
```

### 7.3 Service Request CRUD

**Create**: `app/services/service_crud.py`

```python
"""
Service Request CRUD operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
from geoalchemy2.functions import ST_MakePoint, ST_DWithin
from geoalchemy2.elements import WKTElement

from app.models.service_request import ServiceRequest
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestUpdate

class ServiceCRUD:
    """Service Request CRUD operations"""
    
    @staticmethod
    async def create(db: AsyncSession, service_data: ServiceRequestCreate, requestor_id: UUID) -> ServiceRequest:
        """
        Create new service request
        
        Args:
            db: Database session
            service_data: Service request data
            requestor_id: ID of user creating request
            
        Returns:
            Created service request
        """
        # Create PostGIS point from latitude/longitude
        point = f'POINT({service_data.longitude} {service_data.latitude})'
        
        # Create service request
        db_service = ServiceRequest(
            title=service_data.title,
            description=service_data.description,
            service_type=service_data.service_type,
            priority=service_data.priority,
            location=WKTElement(point, srid=4326),
            location_name=service_data.location_name,
            address=service_data.address,
            requestor_id=requestor_id
        )
        
        db.add(db_service)
        await db.flush()
        await db.refresh(db_service)
        
        return db_service
    
    @staticmethod
    async def get_by_id(db: AsyncSession, request_id: UUID) -> Optional[ServiceRequest]:
        """Get service request by ID"""
        result = await db.execute(
            select(ServiceRequest).where(ServiceRequest.request_id == request_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        service_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ServiceRequest]:
        """
        Get all service requests with filters
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum records to return
            service_type: Filter by service type
            priority: Filter by priority
            status: Filter by status
            
        Returns:
            List of service requests
        """
        query = select(ServiceRequest)
        
        # Apply filters
        if service_type:
            query = query.where(ServiceRequest.service_type == service_type)
        if priority:
            query = query.where(ServiceRequest.priority == priority)
        if status:
            query = query.where(ServiceRequest.status == status)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def nearby(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 50
    ) -> List[ServiceRequest]:
        """
        Find service requests within radius of a point
        
        Args:
            db: Database session
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Radius in kilometers
            limit: Maximum results
            
        Returns:
            List of nearby service requests
        """
        point = ST_MakePoint(longitude, latitude, srid=4326)
        
        query = select(ServiceRequest).where(
            ST_DWithin(
                ServiceRequest.location,
                point,
                radius_km * 1000  # Convert km to meters
            )
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        request_id: UUID,
        status: str,
        provider_id: Optional[UUID] = None
    ) -> Optional[ServiceRequest]:
        """Update service request status"""
        service = await ServiceCRUD.get_by_id(db, request_id)
        if not service:
            return None
        
        service.status = status
        if provider_id:
            service.provider_id = provider_id
        
        await db.flush()
        await db.refresh(service)
        
        return service
```

---

## 8. **Authentication & JWT**

### 8.1 What Is JWT?

**JWT** = JSON Web Token

**Purpose**: Securely identify users without storing sessions

**How it works**:
1. User logs in with email + password
2. Backend creates JWT token containing user info
3. Frontend saves token (localStorage)
4. Frontend includes token in every request
5. Backend verifies token to identify user

### 8.2 Security Functions

**Create**: `app/core/security.py`

```python
"""
Security utilities - Password hashing and JWT tokens
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token (longer expiration)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

## 9. **API Endpoints (FastAPI)**

### 9.1 Main Application

**Create**: `app/main.py`

```python
"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, services

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(services.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IDRM Backend API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

### 9.2 Authentication Endpoints

**Create**: `app/api/v1/auth.py`

```python
"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register new user
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    """
    try:
        # Create user
        user = await UserService.create_user(db, user_data)
        
        # Commit transaction
        await db.commit()
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password
    
    Returns access token and refresh token
    """
    # Authenticate user
    user = await UserService.authenticate(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.user_id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout():
    """Logout (frontend should delete token)"""
    return {"message": "Successfully logged out"}
```

### 9.3 Service Request Endpoints

**Create**: `app/api/v1/services.py`

```python
"""
Service Request API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestResponse,
    ServiceRequestUpdate
)
from app.services.service_crud import ServiceCRUD
from app.core.dependencies import get_current_user  # We'll create this
from app.models.user import User

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("/", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_service_request(
    service_data: ServiceRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new service request
    
    Requires authentication
    """
    try:
        # Create service request
        service = await ServiceCRUD.create(db, service_data, current_user.user_id)
        
        # Commit transaction
        await db.commit()
        
        # Convert to response format
        return service
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service request"
        )

@router.get("/", response_model=List[ServiceRequestResponse])
async def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List service requests with optional filters
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return
    - **service_type**: Filter by service type
    - **priority**: Filter by priority
    - **status**: Filter by status
    """
    services = await ServiceCRUD.get_all(
        db,
        skip=skip,
        limit=limit,
        service_type=service_type,
        priority=priority,
        status=status
    )
    
    return services

@router.get("/{request_id}", response_model=ServiceRequestResponse)
async def get_service(request_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get single service request by ID"""
    service = await ServiceCRUD.get_by_id(db, request_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    return service

@router.get("/nearby/", response_model=List[ServiceRequestResponse])
async def nearby_services(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=100),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Find service requests near a location
    
    - **latitude**: Center latitude
    - **longitude**: Center longitude
    - **radius_km**: Search radius in kilometers
    - **limit**: Maximum results
    """
    services = await ServiceCRUD.nearby(
        db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )
    
    return services

@router.put("/{request_id}/status", response_model=ServiceRequestResponse)
async def update_service_status(
    request_id: UUID,
    status_data: ServiceRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update service request status"""
    service = await ServiceCRUD.update_status(
        db,
        request_id=request_id,
        status=status_data.status,
        provider_id=status_data.provider_id
    )
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    await db.commit()
    return service
```

### 9.4 Authentication Dependency

**Create**: `app/core/dependencies.py`

```python
"""
FastAPI dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services.user_service import UserService

# HTTP Bearer token scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Dependency for protected endpoints
    Usage: current_user: User = Depends(get_current_user)
    """
    # Get token from Authorization header
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = await UserService.get_by_id(db, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user
```

---

## 10. **Geospatial Queries**

### 10.1 PostGIS Functions

**Common spatial queries**:

```python
from geoalchemy2.functions import (
    ST_DWithin,      # Within distance
    ST_Distance,     # Calculate distance
    ST_MakePoint,    # Create point
    ST_AsGeoJSON,    # Convert to GeoJSON
    ST_Contains,     # Point in polygon
    ST_Intersects,   # Geometries intersect
)
```

### 10.2 GeoJSON Endpoint

**Add to** `app/api/v1/services.py`:

```python
from geoalchemy2.functions import ST_AsGeoJSON, ST_X, ST_Y

@router.get("/geojson/", response_class=JSONResponse)
async def services_geojson(
    service_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all service requests as GeoJSON FeatureCollection
    
    Compatible with Leaflet and other mapping libraries
    """
    from sqlalchemy import select, func
    
    # Build query
    query = select(
        ServiceRequest.request_id,
        ServiceRequest.title,
        ServiceRequest.description,
        ServiceRequest.service_type,
        ServiceRequest.priority,
        ServiceRequest.status,
        ST_AsGeoJSON(ServiceRequest.location).label('geojson'),
        ST_X(ServiceRequest.location).label('longitude'),
        ST_Y(ServiceRequest.location).label('latitude')
    )
    
    # Apply filters
    if service_type:
        query = query.where(ServiceRequest.service_type == service_type)
    if priority:
        query = query.where(ServiceRequest.priority == priority)
    if status:
        query = query.where(ServiceRequest.status == status)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Build GeoJSON
    features = []
    for row in rows:
        feature = {
            "type": "Feature",
            "geometry": json.loads(row.geojson),
            "properties": {
                "id": str(row.request_id),
                "title": row.title,
                "description": row.description,
                "service_type": row.service_type,
                "priority": row.priority,
                "status": row.status
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
```

---

## 11. **Testing**

### 11.1 Create Test File

**Create**: `tests/test_auth.py`

```python
"""
Tests for authentication endpoints
"""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "user_id" in data

@pytest.mark.asyncio
async def test_login():
    """Test user login"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First register
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "testpass123",
                "full_name": "Login Test"
            }
        )
        
        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "testpass123"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
```

### 11.2 Run Tests

```bash
# Activate environment
conda activate idrm-backend

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 12. **Deployment**

### 12.1 Running Development Server

```bash
# Activate environment
conda activate idrm-backend

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Your API is now running at:
# http://localhost:8000
# Docs at: http://localhost:8000/docs
```

### 12.2 Production Deployment

**Create**: `run.sh`

```bash
#!/bin/bash
# Production run script

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate idrm-backend

# Run with Uvicorn (production mode)
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --no-access-log
```

Make executable:
```bash
chmod +x run.sh
./run.sh
```

---

## ✅ **Summary**

### What You've Learned

**You can now**:
- ✅ Understand backend architecture
- ✅ Create database models with SQLAlchemy
- ✅ Validate data with Pydantic schemas
- ✅ Build REST APIs with FastAPI
- ✅ Implement JWT authentication
- ✅ Perform geospatial queries
- ✅ Write tests
- ✅ Deploy to production

### What You Built

1. ✅ **Auth Service** - Registration, login, JWT tokens
2. ✅ **Service Management** - CRUD operations, geospatial queries
3. ✅ **Security** - Password hashing, JWT validation
4. ✅ **Database** - SQLAlchemy models with PostGIS

### Files Created

- 📄 `app/main.py` - FastAPI application
- 📄 `app/core/config.py` - Configuration
- 📄 `app/core/security.py` - Security functions
- 📄 `app/db/session.py` - Database session
- 📄 `app/models/user.py` - User model
- 📄 `app/models/service_request.py` - Service model
- 📄 `app/schemas/user.py` - User schemas
- 📄 `app/schemas/service_request.py` - Service schemas
- 📄 `app/services/user_service.py` - User business logic
- 📄 `app/services/service_crud.py` - Service CRUD
- 📄 `app/api/v1/auth.py` - Auth endpoints
- 📄 `app/api/v1/services.py` - Service endpoints

---

## 📖 **What's Next?**

### Build More Services

**Still need**:
- Provider Management Service
- Notifications Service
- Analytics Service
- Admin Service

### Add More Features

- WebSocket for real-time updates
- Background tasks (Celery)
- File uploads (images)
- Email verification
- Password reset
- Rate limiting

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Part of**: IDRM Consolidated Documentation Suite  
**Previous**: [24-FRONTEND-IMPLEMENTATION.md](24-FRONTEND-IMPLEMENTATION.md)  
**Next**: [31-STAGING-SETUP.md](31-STAGING-SETUP.md)  
**Feedback**: Open an issue or submit a PR on GitHub
