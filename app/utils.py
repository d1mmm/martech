import logging
import os
import shutil
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Annotated

import bcrypt
import jwt
from dateutil.parser import parse
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pandas.core.interchange.dataframe_protocol import DataFrame
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.config import KEY, ALGORITHM, JWT_SECRET
from app.db import get_session

import pandas as pd

from app.models import DataFile, FileRecord, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="upload")


def encryption(password):
    return bcrypt.hashpw(password.encode(), KEY).decode()


def insert_into_db(obj, session: Session):
    try:
        session.add(obj)
        session.commit()
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while executing SQL commands: {e}")
        session.rollback()
        raise HTTPException(status_code=502, detail=f'Bad Gateway {e}')
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"File processing error: {e}")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise credentials_exception
    except jwt.exceptions.PyJWTError:
        raise credentials_exception
    user = session.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def check_data_for_nan(df: DataFrame):
    expected_columns = ('Advertiser', 'Brand', 'Start', 'End', 'Format', 'Platform', 'Impr')
    missing_or_empty_columns = []
    for column in expected_columns:
        if column not in df.columns:
            missing_or_empty_columns.append(column)
        elif df[column].isnull().values.any():
            missing_or_empty_columns.append(f"{column} (empty)")
    if missing_or_empty_columns:
        raise ValueError(f"Missing or empty columns: {', '.join(missing_or_empty_columns)}")


def validate_and_parse_date(date_str):
    try:
        return parse(date_str, dayfirst=True)
    except ValueError as v:
       return v


def is_admin(current_user: User):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")


def row_to_dict(row):
    return {
        "year": row.year,
        "total_impressions": row.total_impressions
    }


def add_file_to_db(file: UploadFile, session: Session, user_id: int):
    try:
        filename = file.filename.split('/')[-1]
        data_file = DataFile(
            filename=filename,
            uploaded_by=user_id,
            status="Processing",
            upload_date=datetime.now()
        )
        exist_file = session.query(DataFile).filter(DataFile.filename == filename).first()
        if exist_file:
            raise HTTPException(status_code=409, detail=f"{filename} already exists")
        insert_into_db(data_file, session)
        return pars_file_and_add_records_to_db(file, session, data_file)
    except Exception as e:
        session.rollback()
        logging.error(f"Error processing file: {e}")
        return {"status": "error", "message": f"Error processing file: {str(e)}"}

def pars_file_and_add_records_to_db(file: UploadFile, session: Session, data_file: DataFile):
    with NamedTemporaryFile(delete=False) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_file_path = tmp_file.name
    try:
        df = pd.read_excel(tmp_file_path)
        check_data_for_nan(df)

        for index, row in df.iterrows():
            start_date = validate_and_parse_date(row['Start']) if isinstance(row['Start'], str) else row['Start']
            end_date = validate_and_parse_date(row['End']) if isinstance(row['End'], str) else row['End']

            if not isinstance(start_date, datetime):
                logging.error(start_date)
                continue

            if not isinstance(end_date, datetime):
                logging.error(end_date)
                continue

            record = FileRecord(
                advertiser=row['Advertiser'],
                brand=row['Brand'],
                start=start_date,
                end=end_date,
                format=row['Format'],
                platform=row['Platform'],
                impr=row['Impr'],
                data_file_id=data_file.id
            )
            session.add(record)

        data_file.status = "Completed"
        session.commit()
        return {"status": "success", "message": "File uploaded and processed successfully"}
    except Exception as e:
        session.rollback()
        data_file.status = "Failed"
        data_file.error = str(e)
        session.commit()
        logging.error(f"Error occurred while processing file: {e}")
        return {"status": "error", "message": f"Error occurred while processing file {str(e)}"}
    finally:
        os.remove(tmp_file_path)
