from fastapi import FastAPI, Request, Response, HTTPException, Depends, WebSocket, WebSocketDisconnect
from .routes import interactions
from fastapi.middleware.cors import CORSMiddleware
from .routes import interactions
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time, logging, sqlite3, json, os
from datetime import datetime
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# Import auth and websocket modules
try:
    from .auth import (
        User, UserCreate, UserLogin, Token,
        authenticate_user, create_user, get_user_by_id,
        create_access_token, decode_access_token,
        init_auth_tables, log_audit
    )
    from .websocket import manager, notify_job_status, notify_job_progress
except ImportError:
    # Fallback for development
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from auth import (
        User, UserCreate, UserLogin, Token,
        authenticate_user, create_user, get_user_by_id,
        create_access_token, decode_access_token,
        init_auth_tables, log_audit
    )
    from websocket import manager, notify_job_status, notify_job_progress

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["method", "path"])

# Security
security = HTTPBearer(auto_error=False)

# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    """Get current authenticated user from JWT token"""
    if not credentials:
        return None  # Allow anonymous access for now
    
    token_data = decode_access_token(credentials.credentials)
    if not token_data or not token_data.user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = get_user_by_id(token_data.user_id, DB_PATH)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# FastAPI app with OpenAPI documentation
from app.routes.interactions import router as interactions_router
from app.routes.profile import router as profile_router
app = FastAPI(
    title="Article Eater API",
    description="""
# Article Eater v18.5 - Academic Literature Processing System

## Overview
Article Eater is an AI-powered research automation system that helps students and researchers 
extract evidence-based design principles from academic literature.

## Features
- 📚 **Paper Management**: Search, store, and organize academic papers
- 🔍 **Finding Extraction**: Automated extraction of empirical findings
- 📝 **Rule Synthesis**: Multi-document synthesis with confidence scores
- ⏳ **Job Queue**: Asynchronous processing pipeline (L0-L5)
- 💰 **Cost Tracking**: Monitor API usage and costs
- 👤 **User Profiles**: Manage account and API keys

## Pipeline Stages
- **L0: Harvest** - Gather papers from Semantic Scholar
- **L1: Triage** - Cluster and filter by relevance
- **L2: Extract** - Extract structured findings from full text
- **L3: Synthesize** - Generate rules across multiple papers
- **L4: Expand** - Citation network exploration

## Authentication
Currently in development mode - no authentication required.
Production deployment will use JWT tokens.

## Rate Limits
- Development: No limits
- Production: 100 requests/hour per user

## Support
- Documentation: See GitHub repository
- Issues: Create GitHub issue
- Contact: article-eater@ucsd.edu
    """,
    version="18.5.0",
    contact={
        "name": "Article Eater Team",
        "email": "article-eater@ucsd.edu",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "Health checks and system status"
        },
        {
            "name": "jobs",
            "description": "Job queue management - submit and monitor processing jobs"
        },
        {
            "name": "library",
            "description": "Article library - browse and search papers"
        },
        {
            "name": "findings",
            "description": "Extracted findings from papers"
        },
        {
            "name": "rules",
            "description": "Synthesized rules with evidence"
        },
        {
            "name": "usage",
            "description": "API usage and cost tracking"
        },
        {
            "name": "profile",
            "description": "User profile and preferences"
        },
        {
            "name": "admin",
            "description": "Administrative endpoints (restricted)"
        }
    ],
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc alternative UI
    openapi_url="/openapi.json"
)

# ============================================================================
# CORS CONFIGURATION (Task #2)
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",           # Local development
        "http://localhost:3000",           # Alternative dev port
        "http://127.0.0.1:8080",          # Alternative localhost
        "https://article-eater.ucsd.edu",  # Production
        "*"                                # For initial testing (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],                   # Allow all HTTP methods
    allow_headers=["*"],                   # Allow all headers
)

# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    try: 
        REQUESTS.labels(request.method, request.url.path).inc()
    except Exception: 
        pass
    return response

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
DB_PATH = os.environ.get("DB_PATH", "ae.db")

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class JobSubmit(BaseModel):
    job_type: str
    params: Dict[str, Any]
    priority: int = 100

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class APIKeyAdd(BaseModel):
    provider: str
    key: str

# ============================================================================
# HEALTH & METRICS
# ============================================================================
@app.get("/healthz", tags=["health"], 
         summary="Health Check",
         description="Check if the API is running and responsive")
async def healthz():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "19.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "authentication": True,
            "websockets": True,
            "worker": True
        }
    }

@app.get("/metrics", tags=["health"],
         summary="Prometheus Metrics",
         description="Get Prometheus-compatible metrics for monitoring")
async def metrics():
    """Prometheus metrics"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================
@app.post("/auth/register", tags=["auth"], response_model=User,
          summary="Register New User",
          description="Create a new user account")
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = create_user(user_data, DB_PATH)
        log_audit(user.user_id, "user_registered", details=user.email, db_path=DB_PATH)
        
        logger.info(f"New user registered: {user.email}")
        return user
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", tags=["auth"], response_model=Token,
          summary="User Login",
          description="Authenticate and get access token")
async def login(login_data: UserLogin):
    """Authenticate user and return JWT token"""
    user = authenticate_user(login_data.email, login_data.password, DB_PATH)
    
    if not user:
        log_audit(None, "login_failed", details=login_data.email, db_path=DB_PATH)
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create access token
    access_token = create_access_token(data={
        "sub": user.email,
        "user_id": user.user_id
    })
    
    log_audit(user.user_id, "user_login", details=user.email, db_path=DB_PATH)
    logger.info(f"User logged in: {user.email}")
    
    return Token(access_token=access_token)

@app.get("/auth/me", tags=["auth"], response_model=User,
         summary="Get Current User",
         description="Get currently authenticated user profile")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return current_user

# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time updates
    
    Sends updates about:
    - Job status changes
    - Job progress
    - New articles/findings/rules
    - System notifications
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive messages from client (for heartbeat, etc.)
            data = await websocket.receive_text()
            
            # Echo back for testing
            await manager.send_personal_message({
                "type": "echo",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected: user={user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/ws/stats", tags=["websocket"],
         summary="WebSocket Statistics",
         description="Get current WebSocket connection statistics")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_stats()

# ============================================================================
# JOB QUEUE ENDPOINTS
# ============================================================================
@app.post("/jobs/", tags=["jobs"],
          summary="Submit Job",
          description="Submit a new processing job to the queue",
          response_description="Job created successfully")
async def submit_job(job: JobSubmit):
    """Submit a new processing job"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        job_id = f"job-{int(time.time() * 1000)}"
        
        cursor.execute("""
            INSERT INTO processing_queue 
            (job_id, job_type, params, status, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            job.job_type,
            json.dumps(job.params),
            'pending',
            job.priority,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Job submitted: {job_id} ({job.job_type})")
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Job submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Job submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT job_id, job_type, params, status, priority, 
                   created_at, started_at, completed_at, error
            FROM processing_queue
            WHERE job_id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return dict(row)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/")
async def list_jobs(status: Optional[str] = None, limit: int = 100):
    """List jobs, optionally filtered by status"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT job_id, job_type, params, status, priority, 
                       created_at, started_at, completed_at, error
                FROM processing_queue
                WHERE status = ?
                ORDER BY priority DESC, created_at DESC
                LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT job_id, job_type, params, status, priority, 
                       created_at, started_at, completed_at, error
                FROM processing_queue
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LIBRARY ENDPOINTS
# ============================================================================
@app.get("/library/")
async def list_articles(limit: int = 50, offset: int = 0):
    """List articles in library"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT article_id, doi, title, authors, year, venue, 
                   abstract, citation_count, is_open_access
            FROM articles
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            article = dict(row)
            if article.get('authors'):
                try:
                    article['authors'] = json.loads(article['authors'])
                except:
                    article['authors'] = [article['authors']]
            articles.append(article)
        
        return articles
        
    except Exception as e:
        logger.error(f"Failed to list articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/library/{article_id}")
async def get_article(article_id: str):
    """Get detailed article information"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM articles
            WHERE article_id = ?
        """, (article_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article = dict(row)
        if article.get('authors'):
            try:
                article['authors'] = json.loads(article['authors'])
            except:
                pass
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/library/search")
async def search_articles(q: str, limit: int = 50):
    """Search articles by query"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        search_term = f"%{q}%"
        cursor.execute("""
            SELECT article_id, doi, title, authors, year, venue, 
                   abstract, citation_count, is_open_access
            FROM articles
            WHERE title LIKE ? OR abstract LIKE ? OR doi LIKE ?
            ORDER BY citation_count DESC
            LIMIT ?
        """, (search_term, search_term, search_term, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            article = dict(row)
            if article.get('authors'):
                try:
                    article['authors'] = json.loads(article['authors'])
                except:
                    pass
            articles.append(article)
        
        return articles
        
    except Exception as e:
        logger.error(f"Failed to search articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FINDINGS ENDPOINTS
# ============================================================================
@app.get("/findings")
async def get_findings(article_id: Optional[str] = None, limit: int = 100):
    """Get findings, optionally filtered by article"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if article_id:
            cursor.execute("""
                SELECT *
                FROM findings
                WHERE paper_id = ?
                LIMIT ?
            """, (article_id, limit))
        else:
            cursor.execute("""
                SELECT *
                FROM findings
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        findings = []
        for row in rows:
            finding = dict(row)
            # Parse JSON fields
            for field in ['antecedents']:
                if finding.get(field):
                    try:
                        finding[field] = json.loads(finding[field])
                    except:
                        pass
            findings.append(finding)
        
        return findings
        
    except Exception as e:
        logger.error(f"Failed to get findings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RULES ENDPOINTS
# ============================================================================
@app.get("/rules")
async def list_rules(limit: int = 50):
    """List synthesized rules"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rule_id, rule, confidence, triangulation_score, 
                   contradiction_count, created_at
            FROM rules
            ORDER BY confidence DESC, created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Failed to list rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules/{rule_id}")
async def get_rule(rule_id: str):
    """Get detailed rule information"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM rules
            WHERE rule_id = ?
        """, (rule_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rule = dict(row)
        
        # Get evidence
        cursor.execute("""
            SELECT e.*, a.title, a.authors, a.year
            FROM rule_evidence e
            LEFT JOIN articles a ON e.article_id = a.article_id
            WHERE e.rule_id = ?
        """, (rule_id,))
        
        evidence_rows = cursor.fetchall()
        rule['evidence'] = [dict(r) for r in evidence_rows]
        
        conn.close()
        
        return rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules/{rule_id}/evidence")
async def get_rule_evidence(rule_id: str):
    """Get all evidence for a rule"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*, a.title, a.authors, a.year, a.doi
            FROM rule_evidence e
            LEFT JOIN articles a ON e.article_id = a.article_id
            WHERE e.rule_id = ?
            ORDER BY e.stance DESC, a.year DESC
        """, (rule_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Failed to get rule evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USAGE & COSTS ENDPOINTS
# ============================================================================
@app.get("/usage/me")
async def get_usage():
    """Get current user's usage statistics"""
    # In production, this would filter by authenticated user
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # NOTE usage data for now
        # In production, query actual usage from database
        
        usage = {
            "current_spend": 2.85,
            "budget_limit": 10.00,
            "budget_percent": 28,
            "budget_remaining": 7.15,
            "period_start": "2025-11-01",
            "period_end": "2025-11-30",
            "breakdown": []
        }
        
        conn.close()
        
        return usage
        
    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================
@app.get("/profile")
async def get_profile():
    """Get user profile"""
    # In production, get from authenticated user
    return {
        "name": "Student User",
        "email": "student@ucsd.edu",
        "role": "Student",
        "member_since": "2025-09-15T00:00:00Z",
        "last_login": datetime.now().isoformat()
    }

@app.patch("/profile")
async def update_profile(profile: ProfileUpdate):
    """Update user profile"""
    # In production, update authenticated user's profile
    logger.info(f"Profile update requested: {profile.dict(exclude_none=True)}")
    return {"message": "Profile updated successfully"}

@app.get("/profile/api-keys")
async def list_api_keys():
    """List user's API keys (masked)"""
    # In production, fetch from encrypted storage
    return [
        {
            "provider": "openai",
            "masked_key": "sk-proj-abc...xyz",
            "added_at": "2025-09-20T10:00:00Z",
            "last_used": datetime.now().isoformat(),
            "usage_count": 127,
            "status": "active"
        }
    ]

@app.post("/profile/api-keys")
async def add_api_key(key_data: APIKeyAdd):
    """Add a new API key"""
    # In production, encrypt and store
    logger.info(f"API key added for provider: {key_data.provider}")
    return {"message": "API key added successfully", "provider": key_data.provider}

@app.delete("/profile/api-keys/{provider}")
async def delete_api_key(provider: str):
    """Delete an API key"""
    # In production, remove from storage
    logger.info(f"API key deleted for provider: {provider}")
    return {"message": "API key deleted successfully"}

# ============================================================================
# ADMIN ENDPOINTS (optional)
# ============================================================================
@app.get("/admin/stats")
async def get_admin_stats():
    """Get system-wide statistics (admin only)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        stats = {}
        
        # Count articles
        cursor.execute("SELECT COUNT(*) as count FROM articles")
        stats['total_articles'] = cursor.fetchone()['count']
        
        # Count findings
        cursor.execute("SELECT COUNT(*) as count FROM findings")
        stats['total_findings'] = cursor.fetchone()['count']
        
        # Count rules
        cursor.execute("SELECT COUNT(*) as count FROM rules")
        stats['total_rules'] = cursor.fetchone()['count']
        
        # Count jobs by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM processing_queue
            GROUP BY status
        """)
        stats['jobs_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get admin stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DATABASE AUTO-MIGRATION
# ============================================================================
def auto_migrate_database():
    """Automatically create database schema if needed"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables or 'articles' not in tables:
            logger.info("Database schema not found - initializing...")
            
            # Run init script
            import subprocess
            result = subprocess.run(
                ['python3', 'init_database.py'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)) + '/..'
            )
            
            if result.returncode == 0:
                logger.info("✓ Database initialized successfully")
            else:
                logger.warning(f"Database initialization returned code {result.returncode}")
        else:
            logger.info(f"✓ Database found with {len(tables)} tables")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM articles")
            article_count = cursor.fetchone()[0]
            logger.info(f"  - {article_count} articles")
            
            if article_count == 0:
                logger.warning("  ⚠ Database is empty - run 'python3 init_database.py' to populate")
        
        conn.close()
        
        # Initialize auth tables
        logger.info("Initializing authentication system...")
        init_auth_tables(DB_PATH)
        logger.info("✓ Auth tables initialized")
        
    except Exception as e:
        logger.error(f"Database auto-migration failed: {e}")

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("="*60)
    logger.info("Article Eater API v19.0 starting up...")
    logger.info("="*60)
    logger.info(f"Database: {DB_PATH}")
    logger.info("CORS enabled for local development and production")
    logger.info("Features: Authentication, WebSockets, Real-time updates")
    
    # Auto-migrate database
    auto_migrate_database()
    
    # Start WebSocket heartbeat task
    import asyncio
    from .websocket import heartbeat_task
    asyncio.create_task(heartbeat_task())
    logger.info("✓ WebSocket heartbeat started")
    
    logger.info("="*60)
    logger.info("✓ Startup complete - API ready")
    logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Article Eater API shutting down...")
from .db import ensure_db
from .routes.usage import router as usage_router
from .routes.keys import router as keys_router

try:
    ensure_db()
except Exception:
    pass

app.include_router(usage_router)
app.include_router(keys_router)

# v20.0.1: enable interactions router
app.include_router(interactions.router)

app.include_router(interactions_router)
app.include_router(profile_router)