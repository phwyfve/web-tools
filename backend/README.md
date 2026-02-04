# FastAPI MongoDB Authentication System

A complete authentication system built with FastAPI, MongoDB (via Beanie ODM), and FastAPI-Users for user management and JWT authentication.

## 🏗️ Architecture Overview

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **MongoDB**: Document database for user storage
- **Beanie**: Async ODM (Object Document Mapper) for MongoDB
- **FastAPI-Users**: Pre-built authentication system with JWT support
- **JWT Tokens**: Bearer token authentication for API access

## 📋 API Routes

### **🔐 Authentication Routes**

| Method | Endpoint | Purpose | Authentication |
|--------|----------|---------|----------------|
| `POST` | `/auth/register` | Register a new user | None |
| `POST` | `/auth/jwt/login` | Login and get JWT token | None |
| `POST` | `/auth/jwt/logout` | Logout (invalidate token) | Bearer Token |

**Registration Example:**
```json
POST /auth/register
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Login Example:**
```json
POST /auth/jwt/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### **👤 User Management Routes**

| Method | Endpoint | Purpose | Authentication |
|--------|----------|---------|----------------|
| `GET` | `/users/me` | Get current user profile | Bearer Token |
| `PATCH` | `/users/me` | Update current user profile | Bearer Token |

**User Profile Response:**
```json
{
  "id": "6926c61a8e6d5f56f1ce9f36",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": true,
}
```

### **🛡️ Protected API Routes**

| Method | Endpoint | Purpose | Authentication |
|--------|----------|---------|----------------|
| `GET` | `/api/protected-route` | Example protected endpoint | Bearer Token |
| `GET` | `/api/user-profile` | Get detailed user profile | Bearer Token |

### **📖 Documentation & Health**

| Method | Endpoint | Purpose | Authentication |
|--------|----------|---------|----------------|
| `GET` | `/` | API overview and endpoints | None |
| `GET` | `/docs` | Interactive API documentation (Swagger) | None |
| `GET` | `/health` | Health check endpoint | None |

## 🔧 User Service API

The `user_service.py` provides a high-level Python API for authentication operations:

### **Core Functions:**

#### `authenticate_email_async(email, password, first_name, last_name, create=True)`
- **Purpose**: Universal authentication function
- **Logic**: Try login first, create user if doesn't exist (when `create=True`)
- **Returns**: Session data with JWT token and user profile

#### `register_async(email, password, first_name, last_name)`
- **Purpose**: User registration with automatic login
- **Logic**: Calls `authenticate_email_async` with `create=True`
- **Benefit**: Works even if user already exists (just logs them in)

### **Example Usage:**
```python
from user_service import authenticate_email_async, register_async

# Login existing user or create new one
result = await authenticate_email_async(
    email="user@example.com",
    password="password123",
    first_name="John",
    last_name="Doe",
    create=True
)

if result["success"]:
    token = result["token"]
    user_profile = result["user_profile"]
    print(f"Authenticated: {user_profile['email']}")
```

## 🔐 Authentication Flow

### **1. New User Registration**
```
User → POST /auth/register → User Created → Auto-Login → JWT Token
```

### **2. Existing User Login**
```
User → POST /auth/jwt/login → JWT Token
```

### **3. Protected Route Access**
```
Client → Add "Authorization: Bearer <token>" → Access Granted
```

### **4. User Service Flow**
```
authenticate_email_async() → Try Login → If Failed & create=True → Register → Login → Return Token
```

## 🛠️ Setup & Installation

### **Prerequisites:**
- Python 3.11+
- MongoDB (local installation)

### **Installation:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start MongoDB (Windows)
# MongoDB should be running on localhost:27017

# Start the application
uvicorn main:app --reload
```

### **Testing:**
```bash
# Test the authentication system
python test_api.py

# Test direct token validation
python test_token_direct.py
```

## 🛠️ Configuration

### **Environment Variables:**
```bash
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=fastapi_mongo_test
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### **Default Settings:**
- **Database**: `fastapi_mongo_test`
- **Collection**: `users`
- **JWT Lifetime**: 1 hour (3600 seconds)
- **Default Verification**: Users are verified by default (`is_verified=True`)

## 🚀 Getting Started

### **1. Start the Server:**
```bash
uvicorn main:app --reload
```

### **2. Access Documentation:**
- **Interactive Docs**: http://localhost:8000/docs
- **API Overview**: http://localhost:8000/

### **3. Test Authentication:**
```bash
python test_api.py
```

## 🎯 Key Features

- ✅ **Auto-Registration**: Create users automatically if they don't exist
- ✅ **JWT Authentication**: Secure bearer token system
- ✅ **User Verification**: Users are verified by default for development
- ✅ **Protected Routes**: Easy authorization with dependency injection
- ✅ **MongoDB Integration**: Async document storage with Beanie
- ✅ **API Documentation**: Auto-generated Swagger/OpenAPI docs
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **Type Safety**: Full Pydantic validation and type hints

## 🔄 Next Steps

This authentication system provides a solid foundation for:
- **File Management Apps**: Upload/download with user ownership
- **Multi-tenant Applications**: User-specific data isolation  
- **Web Applications**: Session management with JWT tokens
- **Mobile APIs**: Token-based authentication for mobile apps

---

**Ready for production with proper environment configuration and secret management!** 🎉
