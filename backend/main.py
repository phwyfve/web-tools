from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from core.database import init_db
from core.auth import auth_backend, fastapi_users
from schemas import UserCreate, UserRead, UserUpdate
from core.create_indexes import create_indexes
import traceback
import logging

# Import main routes from api_routes.py file
from routes.api_routes import router

# Import new process management routes from routes/ directory
from routes.merge_pdfs import router as merge_pdfs_router
from routes.split_pdfs import router as split_pdfs_router
from routes.merge_images import router as merge_images_router
from routes.xls_to_pdf import router as xls_to_pdf_router
from routes.commands import router as commands_router
from routes.files import router as files_router
from routes.admin import router as admin_router
from routes.trading_routes import router as trading_router
from routes.youtube_summary import router as youtube_summary_router

# Import cleanup service
from service.cleanup_service import start_cleanup_scheduler
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    
    # Create MongoDB indexes for performance
    print("📊 Creating MongoDB indexes...")
    await create_indexes()
    print("✓ Indexes created successfully")
    
    # Start cleanup scheduler in the background (if enabled)
    if getattr(settings, 'enable_cleanup_scheduler', True):
        #cleanup_task = start_cleanup_scheduler()
        print("🧹 Cleanup scheduler started")
    else:
        print("🚫 Cleanup scheduler disabled")
    
    yield
    # Shutdown (if needed)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('app.log', encoding='utf-8')  # File output
    ]
)

# Create FastAPI app
app = FastAPI(
    title="FastAPI MongoDB File Management App",
    description="A FastAPI application with MongoDB, FastAPI-Users authentication, GridFS file storage, and CORS setup for React frontend.",
    version="1.0.0",
    lifespan=lifespan
)

# Add exception handler to log detailed errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them"""
    error_msg = f"Unhandled exception: {str(exc)}"
    traceback_str = traceback.format_exc()
    
    print(f"ERROR in {request.method} {request.url}")
    print(f"Error: {error_msg}")
    print(f"Traceback:\n{traceback_str}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": error_msg,
            "traceback": traceback_str,
            "path": str(request.url)
        }
    )

# Add CORS middleware to allow React app to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (webapp)
        "http://localhost:3001",  # React dev server (webapp-webtools)
        "http://localhost:3002",  # React dev server (webapp-trading)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Include registration route
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Include user management routes
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include email verification routes
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# Include custom routes
app.include_router(router, prefix="/api", tags=["api"])

# Include process management routes
app.include_router(youtube_summary_router, prefix="/api", tags=["AI Agents"])
app.include_router(merge_pdfs_router, prefix="/api", tags=["Process Management"])
app.include_router(split_pdfs_router, prefix="/api", tags=["Process Management"])
app.include_router(merge_images_router, prefix="/api", tags=["Process Management"])
app.include_router(xls_to_pdf_router, prefix="/api", tags=["Process Management"])
app.include_router(commands_router, prefix="/api", tags=["Process Management"])
app.include_router(files_router, prefix="/api", tags=["File Downloads"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
app.include_router(trading_router, prefix="/api", tags=["Trading"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI with MongoDB and FastAPI-Users!",
        "docs": "/docs",
        "auth_endpoints": {
            "register": "/auth/register",
            "login": "/auth/jwt/login",
            "logout": "/auth/jwt/logout"
        },
        "user_endpoints": {
            "me": "/users/me",
            "protected_route": "/api/protected-route",
            "user_profile": "/api/user-profile"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
