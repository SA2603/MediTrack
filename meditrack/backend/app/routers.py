from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models as m, schemas as s
from .auth import hash_pw, verify_pw, make_token, current_user, require
from .database import get_db

r = APIRouter(prefix="/api")
SLOTS = [f"{h:02d}:{mi:02d}" for h in range(9, 17) for mi in (0, 30)]

def uo(u): return {"id": u.id, "name": u.name, "email": u.email, "role": u.role, "phone": u.phone}
def pat(db, u): return db.query(m.Patient).filter_by(user_id=u.id).first()
def doc(db, u): return db.query(m.Doctor).filter_by(user_id=u.id).first()
def dj(d): return {"id": d.id, "name": d.user.name, "specialization": d.specialization, "qualification": d.qualification, "experience": d.experience, "availability": d.availability}
def aj(a): return {"id": a.id, "patient_id": a.patient_id, "patient": a.patient.user.name, "doctor_id": a.doctor_id, "doctor": a.doctor.user.name, "date": str(a.appointment_date), "time": a.appointment_time.strftime("%H:%M"), "reason": a.reason, "status": a.status}
def rj(x): return {"id": x.id, "patient_id": x.patient_id, "patient": x.patient.user.name, "doctor": x.doctor.user.name, "diagnosis": x.diagnosis, "notes": x.notes, "date": x.record_date.date().isoformat()}
def pj(x): return {"id": x.id, "patient_id": x.patient_id, "patient": x.patient.user.name, "doctor": x.doctor.user.name, "appointment_id": x.appointment_id, "medicine_name": x.medicine_name, "dosage": x.dosage, "frequency": x.frequency, "duration": x.duration, "instructions": x.instructions, "date": x.created_at.date().isoformat()}

def new_user(db, d, role):
    if db.query(m.User).filter_by(email=d.email.lower()).first():
        raise HTTPException(409, "Email already registered")
    u = m.User(name=d.name, email=d.email.lower(), password_hash=hash_pw(d.password), role=role, phone=d.phone)
    db.add(u); db.flush()
    return u

# ---------- Auth ----------
@r.post("/auth/register", status_code=201)
def register(d: s.Register, db: Session = Depends(get_db)):
    u = new_user(db, d, "PATIENT"); db.add(m.Patient(user_id=u.id)); db.commit()
    return {"access_token": make_token(u), "token_type": "bearer", "user": uo(u)}

@r.post("/auth/login")
def login(d: s.Login, db: Session = Depends(get_db)):
    u = db.query(m.User).filter_by(email=d.email.lower()).first()
    if not u or not verify_pw(d.password, u.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": make_token(u), "token_type": "bearer", "user": uo(u)}

@r.get("/auth/me")
def me(u=Depends(current_user), db: Session = Depends(get_db)):
    out = uo(u)
    p = pat(db, u) if u.role == "PATIENT" else None
    if p: out["profile"] = {"date_of_birth": str(p.date_of_birth or ""), "gender": p.gender, "blood_group": p.blood_group, "address": p.address, "emergency_contact": p.emergency_contact}
    return out

@r.put("/auth/me")
def update_me(d: s.ProfileUpdate, u=Depends(current_user), db: Session = Depends(get_db)):
    data = d.model_dump(exclude_unset=True)
    for k in ("name", "phone"):
        if data.get(k): setattr(u, k, data[k])
    p = pat(db, u)
    if p:
        for k in ("date_of_birth", "gender", "blood_group", "address", "emergency_contact"):
            if k in data: setattr(p, k, data[k])
    db.commit()
    return uo(u)

# ---------- Doctors ----------
@r.get("/doctors")
def doctors(_=Depends(current_user), db: Session = Depends(get_db)):
    return [dj(d) for d in db.query(m.Doctor).all()]

@r.get("/doctors/{id}")
def doctor(id: int, _=Depends(current_user), db: Session = Depends(get_db)):
    d = db.get(m.Doctor, id)
    if not d: raise HTTPException(404, "Doctor not found")
    return dj(d)

@r.get("/doctors/{id}/slots")
def slots(id: int, date: date, _=Depends(current_user), db: Session = Depends(get_db)):
    taken = {a.appointment_time.strftime("%H:%M") for a in db.query(m.Appointment).filter(
        m.Appointment.doctor_id == id, m.Appointment.appointment_date == date, m.Appointment.status != "CANCELLED")}
    return [t for t in SLOTS if t not in taken]

# ---------- Appointments ----------
@r.get("/appointments")
def appointments(u=Depends(current_user), db: Session = Depends(get_db)):
    q = db.query(m.Appointment)
    if u.role == "PATIENT": q = q.filter_by(patient_id=pat(db, u).id)
    elif u.role == "DOCTOR": q = q.filter_by(doctor_id=doc(db, u).id)
    return [aj(a) for a in q.order_by(m.Appointment.appointment_date.desc(), m.Appointment.appointment_time.desc())]

@r.post("/appointments", status_code=201)
def book(d: s.AppointmentIn, u=Depends(require("PATIENT")), db: Session = Depends(get_db)):
    if d.appointment_date < date.today(): raise HTTPException(400, "Date cannot be in the past")
    if not db.get(m.Doctor, d.doctor_id): raise HTTPException(404, "Doctor not found")
    if db.query(m.Appointment).filter(m.Appointment.doctor_id == d.doctor_id, m.Appointment.appointment_date == d.appointment_date,
            m.Appointment.appointment_time == d.appointment_time, m.Appointment.status != "CANCELLED").first():
        raise HTTPException(409, "That time slot is already booked")
    a = m.Appointment(patient_id=pat(db, u).id, doctor_id=d.doctor_id, appointment_date=d.appointment_date, appointment_time=d.appointment_time, reason=d.reason)
    db.add(a); db.commit(); db.refresh(a)
    return aj(a)

@r.put("/appointments/{id}")
def set_status(id: int, d: s.StatusIn, u=Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(m.Appointment, id)
    if not a: raise HTTPException(404, "Appointment not found")
    if u.role == "PATIENT":
        if a.patient_id != pat(db, u).id: raise HTTPException(403, "Not your appointment")
        if d.status != "CANCELLED" or a.status != "PENDING": raise HTTPException(400, "Patients can only cancel pending appointments")
    elif u.role == "DOCTOR" and a.doctor_id != doc(db, u).id:
        raise HTTPException(403, "Not your appointment")
    a.status = d.status; db.commit()
    return aj(a)

@r.delete("/appointments/{id}", status_code=204)
def delete_appt(id: int, _=Depends(require("ADMIN")), db: Session = Depends(get_db)):
    a = db.get(m.Appointment, id)
    if not a: raise HTTPException(404, "Appointment not found")
    db.delete(a); db.commit()

# ---------- Patients (doctor view) ----------
@r.get("/patients/{id}")
def patient_detail(id: int, u=Depends(require("DOCTOR", "ADMIN")), db: Session = Depends(get_db)):
    p = db.get(m.Patient, id)
    if not p: raise HTTPException(404, "Patient not found")
    if u.role == "DOCTOR" and not db.query(m.Appointment).filter_by(doctor_id=doc(db, u).id, patient_id=id).first():
        raise HTTPException(403, "No appointment relationship with this patient")
    return {"id": p.id, "name": p.user.name, "email": p.user.email, "phone": p.user.phone, "date_of_birth": str(p.date_of_birth or ""),
            "gender": p.gender, "blood_group": p.blood_group, "address": p.address, "emergency_contact": p.emergency_contact}

# ---------- Records & Prescriptions ----------
def scoped(db, u, Model):
    q = db.query(Model)
    if u.role == "PATIENT": q = q.filter_by(patient_id=pat(db, u).id)
    elif u.role == "DOCTOR": q = q.filter_by(doctor_id=doc(db, u).id)
    return q

def check_relation(db, d, patient_id):
    if not db.query(m.Appointment).filter_by(doctor_id=d.id, patient_id=patient_id).first():
        raise HTTPException(403, "You can only add data for patients with whom you have an appointment")

@r.get("/medical-records")
def records(u=Depends(current_user), db: Session = Depends(get_db)):
    return [rj(x) for x in scoped(db, u, m.MedicalRecord).order_by(m.MedicalRecord.record_date.desc())]

@r.post("/medical-records", status_code=201)
def add_record(d: s.RecordIn, u=Depends(require("DOCTOR")), db: Session = Depends(get_db)):
    me_ = doc(db, u); check_relation(db, me_, d.patient_id)
    x = m.MedicalRecord(patient_id=d.patient_id, doctor_id=me_.id, diagnosis=d.diagnosis, notes=d.notes)
    db.add(x); db.commit(); db.refresh(x)
    return rj(x)

@r.get("/prescriptions")
def prescriptions(u=Depends(current_user), db: Session = Depends(get_db)):
    return [pj(x) for x in scoped(db, u, m.Prescription).order_by(m.Prescription.created_at.desc())]

@r.post("/prescriptions", status_code=201)
def add_rx(d: s.PrescriptionIn, u=Depends(require("DOCTOR")), db: Session = Depends(get_db)):
    me_ = doc(db, u); check_relation(db, me_, d.patient_id)
    if d.appointment_id:
        a = db.get(m.Appointment, d.appointment_id)
        if not a or a.doctor_id != me_.id or a.patient_id != d.patient_id: raise HTTPException(400, "Invalid appointment")
    x = m.Prescription(doctor_id=me_.id, **d.model_dump())
    db.add(x); db.commit(); db.refresh(x)
    return pj(x)

@r.delete("/prescriptions/{id}", status_code=204)
def del_rx(id: int, u=Depends(require("DOCTOR")), db: Session = Depends(get_db)):
    x = db.get(m.Prescription, id)
    if not x or x.doctor_id != doc(db, u).id: raise HTTPException(404, "Prescription not found")
    db.delete(x); db.commit()

# ---------- Doctor dashboard ----------
@r.get("/doctor/stats")
def doctor_stats(u=Depends(require("DOCTOR")), db: Session = Depends(get_db)):
    q = db.query(m.Appointment).filter_by(doctor_id=doc(db, u).id)
    return {"today": q.filter_by(appointment_date=date.today()).count(), "pending": q.filter_by(status="PENDING").count(),
            "completed": q.filter_by(status="COMPLETED").count(), "total_patients": q.with_entities(m.Appointment.patient_id).distinct().count()}

# ---------- Admin ----------
@r.get("/admin/statistics")
def stats(_=Depends(require("ADMIN")), db: Session = Depends(get_db)):
    cnt = lambda M, **f: db.query(M).filter_by(**f).count()
    by_status = {k: cnt(m.Appointment, status=k) for k in ("PENDING", "CONFIRMED", "COMPLETED", "CANCELLED")}
    since = date.today() - timedelta(days=29)
    over = db.query(m.Appointment.appointment_date, func.count()).filter(m.Appointment.appointment_date >= since).group_by(m.Appointment.appointment_date).order_by(m.Appointment.appointment_date).all()
    return {"total_users": cnt(m.User), "total_patients": cnt(m.Patient), "total_doctors": cnt(m.Doctor), "total_appointments": cnt(m.Appointment),
            "pending_appointments": by_status["PENDING"], "completed_appointments": by_status["COMPLETED"],
            "appointments_by_status": by_status, "appointments_over_time": [{"date": str(d), "count": c} for d, c in over]}

@r.get("/admin/users")
def users(_=Depends(require("ADMIN")), db: Session = Depends(get_db)):
    return [uo(u) for u in db.query(m.User).order_by(m.User.id)]

@r.delete("/admin/users/{id}", status_code=204)
def del_user(id: int, a=Depends(require("ADMIN")), db: Session = Depends(get_db)):
    u = db.get(m.User, id)
    if not u: raise HTTPException(404, "User not found")
    if u.id == a.id: raise HTTPException(400, "You cannot delete yourself")
    for M, fk in ((m.Patient, "patient"), (m.Doctor, "doctor")):
        x = db.query(M).filter_by(user_id=id).first()
        if x:
            for T in (m.Appointment, m.MedicalRecord, m.Prescription):
                db.query(T).filter_by(**{fk + "_id": x.id}).delete()
            db.delete(x)
    db.delete(u); db.commit()

@r.get("/admin/patients")
def all_patients(_=Depends(require("ADMIN")), db: Session = Depends(get_db)):
    return [{"id": p.id, "name": p.user.name, "email": p.user.email, "phone": p.user.phone, "gender": p.gender, "blood_group": p.blood_group} for p in db.query(m.Patient)]

@r.post("/admin/doctors", status_code=201)
def create_doctor(d: s.NewDoctor, _=Depends(require("ADMIN")), db: Session = Depends(get_db)):
    u = new_user(db, d, "DOCTOR")
    x = m.Doctor(user_id=u.id, specialization=d.specialization, qualification=d.qualification, experience=d.experience, availability=d.availability)
    db.add(x); db.commit(); db.refresh(x)
    return dj(x)
