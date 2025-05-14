from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import SessionLocal
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from app.database import get_db
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
'''@router.post("/register")
def register(user: schemas.UserCreate):
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = next(get_db())
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = auth.hash_password(user.password)
    role = "admin" if "@admin.com" in user.email else "user" 
    
    if "@admin.com" in user.email:
        role="admin"
    elif "@organizer.com" in user.email:
        role="organizer"
    else:
        role="user"       
    new_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_pwd,
        #role=role
        Roleid=user.roleid     
    )
    db.add(new_user)
    db.commit()
    return {"message": f"User registered successfully as {role}"}'''
    
@router.post("/register")
def register(user: schemas.UserCreate):
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = next(get_db())
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_pwd = auth.hash_password(user.password)
        role_name = db.query(models.Role).filter(models.Role.roleid == user.roleid).first()
        if not role_name:
            raise HTTPException(status_code=400, detail="Invalid role id")
        new_user = models.User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            hashed_password=hashed_pwd,
            roleid=user.roleid
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": f"User registered successfully as {role_name.rolename}"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.post("/login")
async def login(request: Request):
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    db = next(get_db())
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        username = form.get("username")
        password = form.get("password") 
    elif "application/json" in content_type:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")    
    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest):
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    db = next(get_db())
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = auth.create_reset_token(request.email)
    return {"reset_token": reset_token, "message": "Use this token to reset password within 15 minutes"}

@router.post("/reset-password")
def reset_password(request: schemas.ResetPasswordRequest):
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = next(get_db())

    email = auth.verify_reset_token(request.token)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = pwd_context.hash(request.new_password)
    db.commit()
    return {"message": "Password reset successful"}
  


