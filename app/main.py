import logging
from datetime import datetime, timedelta
from typing import Annotated

import jwt
import uvicorn
from fastapi import FastAPI, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.config import JWT_SECRET, ALGORITHM
from app.db import get_session
from app.models import User, FileRecord, DataFile
from app.utils import encryption, insert_into_db, get_current_user, add_file_to_db, row_to_dict, is_admin

logging.basicConfig(filename='martech.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def read_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], name: str = Form(...),
                        session: Session = Depends(get_session)):
    username_email = session.query(User).filter(User.username == form_data.username).first()
    if username_email:
        raise HTTPException(status_code=409, detail=f"User already exists with {form_data.username}")
    is_admin = True if "admin" in form_data.password.lower() else False
    hashed_password = encryption(form_data.password)
    new_user = User(name=name, username=form_data.username, hashed_password=hashed_password, is_admin=is_admin)
    insert_into_db(new_user, session)
    return {"message": "User registered successfully"}


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    hashed_password = encryption(form_data.password)
    user = session.query(User).filter(User.username == form_data.username, User.hashed_password == hashed_password).first()
    if not user:
        raise HTTPException(status_code=401, detail=f"The credentials are invalid")

    payload = {
        "username": user.username,
        "exp": datetime.now() + timedelta(minutes=5)
    }
    access_token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer", "message": f"{user.name} login successfully",
            "is_admin": user.is_admin}


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/upload")
async def get_upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def upload_file(current_user: Annotated[User, Depends(get_current_user)], file: UploadFile = File(...),
                      session: Session = Depends(get_session)):
    if not file:
        raise HTTPException(status_code=400, detail="File is required")
    summary = add_file_to_db(file, session, user_id=current_user.id)
    if summary['status'] == 'error':
        raise HTTPException(status_code=400, detail=summary['message'])
    return {}


@app.get("/results", response_class=HTMLResponse)
async def get_aggregated_results(request: Request, session: Session = Depends(get_session)):
    results = session.query(
        func.extract('year', FileRecord.start).label('year'),
        func.sum(FileRecord.impr).label('total_impressions')
    ).group_by(func.extract('year', FileRecord.start)).all()
    results_dict = [row_to_dict(row) for row in results]
    return templates.TemplateResponse("results.html", {"request": request, "results": results_dict})


@app.get("/admin/log-files", response_class=HTMLResponse)
async def log_files_page(request: Request, session: Session = Depends(get_session)):
    logs = session.query(DataFile).all()
    return templates.TemplateResponse("admin_log_files.html", {"request": request, "logs": logs})


@app.get("/admin/full-data", response_class=HTMLResponse)
async def full_data_page(request: Request, session: Session = Depends(get_session)):
    file_records = session.query(FileRecord).all()
    return templates.TemplateResponse("admin_full_data.html", {"request": request, "file_records": file_records})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")