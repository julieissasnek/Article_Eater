"""
Article Eater V22.0.0 (Post-Quinean) - Authentication System
JWT-based authentication with user management
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
import jwt
import secrets
import sqlite3
import json
from pydantic import BaseModel, EmailStr

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    name: str
    role: str = "student"


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload"""
    email: Optional[str] = None
    user_id: Optional[str] = None


class User(BaseModel):
    """User model"""
    user_id: str
    email: str
    name: str
    role: str
    created_at: str
    last_login: Optional[str] = None


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN UTILITIES
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None:
            return None
        
        return TokenData(email=email, user_id=user_id)
        
    except jwt.PyJWTError:
        return None


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

def init_auth_tables(db_path: str = "./ae.db"):
    """Initialize authentication tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TEXT DEFAULT (datetime('now')),
            last_login TEXT,
            is_active BOOLEAN DEFAULT 1,
            preferences TEXT
        )
    """)
    
    # User API keys table (for storing encrypted API keys per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            encrypted_key TEXT NOT NULL,
            masked_key TEXT NOT NULL,
            added_at TEXT DEFAULT (datetime('now')),
            last_used TEXT,
            usage_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, provider)
        )
    """)
    
    # Sessions table (for token blacklisting/logout)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,
            is_valid BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Audit log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            ip_address TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
        )
    """)
    
    conn.commit()
    conn.close()


# ============================================================================
# USER CRUD OPERATIONS
# ============================================================================

def create_user(user_data: UserCreate, db_path: str = "./ae.db") -> User:
    """Create a new user"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT 1 FROM users WHERE email = ?", (user_data.email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("User with this email already exists")
    
    # Generate user ID
    user_id = f"user-{secrets.token_urlsafe(8)}"
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Insert user
    cursor.execute("""
        INSERT INTO users (user_id, email, hashed_password, name, role)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, user_data.email, hashed_password, user_data.name, user_data.role))
    
    conn.commit()
    
    # Fetch created user
    cursor.execute("""
        SELECT user_id, email, name, role, created_at, last_login
        FROM users WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return User(
        user_id=row[0],
        email=row[1],
        name=row[2],
        role=row[3],
        created_at=row[4],
        last_login=row[5]
    )


def authenticate_user(email: str, password: str, db_path: str = "./ae.db") -> Optional[User]:
    """Authenticate a user and return user object"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email, hashed_password, name, role, created_at, last_login
        FROM users
        WHERE email = ? AND is_active = 1
    """, (email,))
    
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Verify password
    if not verify_password(password, row[2]):
        conn.close()
        return None
    
    # Update last login
    cursor.execute("""
        UPDATE users SET last_login = ? WHERE user_id = ?
    """, (datetime.now().isoformat(), row[0]))
    
    conn.commit()
    conn.close()
    
    return User(
        user_id=row[0],
        email=row[1],
        name=row[3],
        role=row[4],
        created_at=row[5],
        last_login=datetime.now().isoformat()
    )


def get_user_by_id(user_id: str, db_path: str = "./ae.db") -> Optional[User]:
    """Get user by ID"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email, name, role, created_at, last_login
        FROM users
        WHERE user_id = ? AND is_active = 1
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return User(
        user_id=row[0],
        email=row[1],
        name=row[2],
        role=row[3],
        created_at=row[4],
        last_login=row[5]
    )


def get_user_by_email(email: str, db_path: str = "./ae.db") -> Optional[User]:
    """Get user by email"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email, name, role, created_at, last_login
        FROM users
        WHERE email = ? AND is_active = 1
    """, (email,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return User(
        user_id=row[0],
        email=row[1],
        name=row[2],
        role=row[3],
        created_at=row[4],
        last_login=row[5]
    )


# ============================================================================
# AUDIT LOGGING
# ============================================================================

def log_audit(user_id: str, action: str, resource: Optional[str] = None,
              details: Optional[str] = None, ip_address: Optional[str] = None,
              db_path: str = "./ae.db"):
    """Log an audit event"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log (user_id, action, resource, details, ip_address)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action, resource, details, ip_address))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Audit logging error: {e}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_default_admin(db_path: str = "./ae.db"):
    """Create default admin user (for initial setup)"""
    try:
        admin_data = UserCreate(
            email="admin@ucsd.edu",
            password="changeme123",  # Should be changed immediately
            name="System Administrator",
            role="admin"
        )
        
        create_user(admin_data, db_path)
        print("✅ Default admin created: admin@ucsd.edu / changeme123")
        print("⚠️  Please change the default password immediately!")
        
    except ValueError:
        print("ℹ️  Admin user already exists")


if __name__ == "__main__":
    """Initialize auth system and create default admin"""
    print("Initializing authentication system...")
    
    init_auth_tables()
    print("✅ Auth tables created")
    
    create_default_admin()
    print("✅ Auth system ready")
