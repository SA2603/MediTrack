from datetime import date, time
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

class Register(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: Optional[str] = None

class Login(BaseModel):
    email: EmailStr
    password: str

class NewDoctor(Register):
    specialization: str
    qualification: str = ""
    experience: int = 0
    availability: str = "Mon-Fri 09:00-17:00"

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None

class AppointmentIn(BaseModel):
    doctor_id: int
    appointment_date: date
    appointment_time: time
    reason: str = Field(min_length=3, max_length=500)

class StatusIn(BaseModel):
    status: Literal["CONFIRMED", "CANCELLED", "COMPLETED"]

class RecordIn(BaseModel):
    patient_id: int
    diagnosis: str = Field(min_length=2, max_length=300)
    notes: str = ""

class PrescriptionIn(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    medicine_name: str = Field(min_length=2)
    dosage: str
    frequency: str
    duration: str
    instructions: str = ""
