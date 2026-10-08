from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(10), index=True, nullable=False)  # PATIENT | DOCTOR | ADMIN
    phone = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialization = Column(String(120), index=True)
    qualification = Column(String(200))
    experience = Column(Integer, default=0)
    availability = Column(String(200), default="Mon-Fri 09:00-17:00")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    blood_group = Column(String(5))
    address = Column(String(300))
    emergency_contact = Column(String(100))
    user = relationship("User")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False)
    appointment_date = Column(Date, index=True, nullable=False)
    appointment_time = Column(Time, nullable=False)
    reason = Column(Text)
    status = Column(String(10), default="PENDING", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient")
    doctor = relationship("Doctor")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False)
    diagnosis = Column(String(300), nullable=False)
    notes = Column(Text)
    record_date = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient")
    doctor = relationship("Doctor")

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    medicine_name = Column(String(200), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(100))
    duration = Column(String(100))
    instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient")
    doctor = relationship("Doctor")
