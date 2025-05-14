from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import schemas, models, auth
from app.database import SessionLocal, get_db
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from app.auth import SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme)):
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = next(get_db())
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")

    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def admin(user: models.User):
    return user.role == "admin"

def org(user:models.User):
    return user.role=="organizer"

def adm_org(user:models.User):
    return user.role in ["admin","organizer"]

@router.get("/users", response_model=list[schemas.ShowUser])
def get_users(current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["admin", "organizer"]:
        raise HTTPException(status_code=403, detail="Only admin or organizer can view users")

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = next(get_db())
    return db.query(models.User).all()

@router.get("/users/{user_id}", response_model=schemas.ShowUser)
def getsingleuser(user_id: int, current_user: models.User = Depends(get_current_user)):
    try:
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        db = next(get_db())
        if not current_user.role or current_user.role.rolename not in ["admin", "organizer"]:
            raise HTTPException(status_code=403, detail="Not authorized to access")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/users")
def create_user(user: schemas.UserCreate,current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["admin", "organizer"]:
        raise HTTPException(status_code=403, detail="Only admin or organizer can create users")
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = next(get_db())
    hashed_pwd = auth.hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@router.put("/users/{user_id}")
def update_user(user_id: int, user: schemas.UserUpdate, current_user: models.User = Depends(get_current_user)):
    if not admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can update users")
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    db = next(get_db())
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db_user.phone = user.phone
    db.commit()
    return {"message": "User updated"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: models.User = Depends(get_current_user)):
    if not admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    db = next(get_db())
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
@router.post("/addaddress", response_model=schemas.ShowAddress)
def addaddress(request: schemas.AddressCreate, current_user: models.User = Depends(get_current_user)):
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Only users can add addresses")
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = next(get_db())

    newaddress = models.Address(
        addressLine_1=request.addressLine_1,
        addressLine_2=request.addressLine_2,
        city=request.city,
        state=request.state,
        zipcode=request.zipcode,
        user_id=current_user.id
    )
    db.add(newaddress)
    db.commit()
    db.refresh(newaddress)
    return newaddress

@router.get("/viewaddresses", response_model=list[schemas.ShowAddress])
def getaddresses(current_user: models.User = Depends(get_current_user)):
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    db = next(get_db())
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Only users can view their addresses")
    addresses = db.query(models.Address).filter(models.Address.user_id == current_user.id).all()
    return addresses




    