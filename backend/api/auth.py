from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib
from database.db_config import DB_PATH

router = APIRouter()

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class UpdateProfile(BaseModel):
    username: str
    email: str
    contact_number: str
    profile_pic: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register")
def register(user: RegisterUser):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(user.password)
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", 
                       (user.username, user.email, pw_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    conn.close()
    return {"message": "User registered successfully!"}

@router.post("/login")
def login(user: LoginUser):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    pw_hash = hash_password(user.password)
    
    cursor.execute("SELECT id, username, email, contact_number, profile_pic FROM users WHERE email=? AND password_hash=?", 
                   (user.email, pw_hash))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    return {
        "message": "Login successful",
        "token": f"mock-jwt-token-{row[0]}",
        "user": {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "contact_number": row[3] or "",
            "profile_pic": row[4] or ""
        }
    }

@router.put("/profile/{user_id}")
def update_profile(user_id: int, profile: UpdateProfile):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET username=?, email=?, contact_number=?, profile_pic=? 
        WHERE id=?
    """, (profile.username, profile.email, profile.contact_number, profile.profile_pic, user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    conn.commit()
    conn.close()
    return {"message": "Profile updated successfully!"}
