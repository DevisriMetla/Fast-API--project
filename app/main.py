from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import database, models, crud
from app.routes import auth, users
from app.database import SessionLocal, get_db
models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)


