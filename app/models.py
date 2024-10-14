from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base, engine
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())



class DataFile(Base):
    __tablename__ = "data_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    uploaded_by = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.now())
    status = Column(String)
    error = Column(String, nullable=True)
    records = relationship("FileRecord", back_populates="data_file")


class FileRecord(Base):
    __tablename__ = 'file_records'

    id = Column(Integer, primary_key=True, index=True)
    advertiser = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    start = Column(Date, nullable=False)
    end = Column(Date, nullable=False)
    format = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    impr = Column(Float, nullable=False)
    data_file_id = Column(Integer, ForeignKey('data_files.id'))
    data_file = relationship("DataFile", back_populates="records")

Base.metadata.create_all(bind=engine)

