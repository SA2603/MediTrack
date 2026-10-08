"""Reset + reseed: python -m app.seed   (demo password: Demo@1234)"""
from datetime import date, time, timedelta
from .database import Base, engine, SessionLocal
from . import models as m
from .auth import hash_pw

PW = "Demo@1234"
Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
db = SessionLocal()
def user(n, e, role):
    u = m.User(name=n, email=e, password_hash=hash_pw(PW), role=role, phone="555-0100"); db.add(u); db.flush(); return u
user("Admin", "admin@meditrack.com", "ADMIN")
docs = [m.Doctor(user_id=user(n, e, "DOCTOR").id, specialization=sp, qualification=q, experience=x) for n, e, sp, q, x in
        [("Dr. Sarah Lee", "doctor@meditrack.com", "Cardiology", "MD, DM Cardiology", 12), ("Dr. Raj Patel", "doctor2@meditrack.com", "Dermatology", "MD Dermatology", 8)]]
db.add_all(docs)
pats = [m.Patient(user_id=user(n, e, "PATIENT").id, gender=g, blood_group=b) for n, e, g, b in
        [("John Carter", "patient@meditrack.com", "Male", "O+"), ("Mia Wong", "patient2@meditrack.com", "Female", "A+"), ("Aman Singh", "patient3@meditrack.com", "Male", "B+"),
         ("Elena Cruz", "patient4@meditrack.com", "Female", "AB-"), ("Omar Ali", "patient5@meditrack.com", "Male", "O-")]]
db.add_all(pats); db.flush()
t = date.today()
for i, (p, d, off, st) in enumerate([(0, 0, 1, "PENDING"), (0, 0, -7, "COMPLETED"), (1, 0, 0, "CONFIRMED"), (2, 1, 2, "PENDING"), (3, 1, -3, "COMPLETED"), (4, 0, -1, "CANCELLED")]):
    db.add(m.Appointment(patient_id=pats[p].id, doctor_id=docs[d].id, appointment_date=t + timedelta(days=off), appointment_time=time(9 + i, 0), reason="Routine consultation", status=st))
db.flush()
db.add(m.MedicalRecord(patient_id=pats[0].id, doctor_id=docs[0].id, diagnosis="Mild hypertension", notes="Advised diet changes; recheck in 4 weeks."))
db.add(m.MedicalRecord(patient_id=pats[3].id, doctor_id=docs[1].id, diagnosis="Contact dermatitis", notes="Avoid irritants."))
db.add(m.Prescription(patient_id=pats[0].id, doctor_id=docs[0].id, medicine_name="Amlodipine", dosage="5 mg", frequency="Once daily", duration="30 days", instructions="Take in the morning."))
db.commit(); print("Seeded. Password for all demo users:", PW)
