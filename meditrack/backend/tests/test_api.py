import os, tempfile
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "t.db")
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app import models as m
from app.database import SessionLocal
from app.auth import hash_pw

c = TestClient(app)
PW = "Passw0rd!"
H = lambda t: {"Authorization": "Bearer " + t}
DAY = str(date.today() + timedelta(days=3))

def mk(role, email):
    db = SessionLocal(); u = m.User(name=role.title(), email=email, password_hash=hash_pw(PW), role=role); db.add(u); db.flush()
    if role == "DOCTOR": db.add(m.Doctor(user_id=u.id, specialization="GP"))
    db.commit(); db.close()
def login(e): return c.post("/api/auth/login", json={"email": e, "password": PW}).json()["access_token"]

def test_register_login_me():
    r = c.post("/api/auth/register", json={"name": "Pat One", "email": "p1@x.com", "password": PW}); assert r.status_code == 201
    assert c.post("/api/auth/register", json={"name": "Pat One", "email": "p1@x.com", "password": PW}).status_code == 409
    assert c.post("/api/auth/login", json={"email": "p1@x.com", "password": "wrong-pass"}).status_code == 401
    t = login("p1@x.com"); me = c.get("/api/auth/me", headers=H(t)); assert me.status_code == 200 and me.json()["role"] == "PATIENT"

def test_auth_required():
    assert c.get("/api/appointments").status_code == 401
    assert c.get("/api/appointments", headers=H("garbage")).status_code == 401

def test_role_access():
    mk("DOCTOR", "d1@x.com"); mk("ADMIN", "a1@x.com")
    p, d, a = login("p1@x.com"), login("d1@x.com"), login("a1@x.com")
    assert c.get("/api/admin/statistics", headers=H(p)).status_code == 403
    assert c.get("/api/admin/statistics", headers=H(d)).status_code == 403
    assert c.get("/api/admin/statistics", headers=H(a)).status_code == 200
    assert c.post("/api/medical-records", headers=H(p), json={"patient_id": 1, "diagnosis": "x"}).status_code == 403

def test_appointment_workflow():
    p, d = login("p1@x.com"), login("d1@x.com"); body = {"doctor_id": 1, "appointment_date": DAY, "appointment_time": "10:00:00", "reason": "Checkup"}
    r = c.post("/api/appointments", headers=H(p), json=body); assert r.status_code == 201; aid = r.json()["id"]
    assert c.post("/api/appointments", headers=H(p), json=body).status_code == 409          # duplicate slot
    assert c.post("/api/appointments", headers=H(d), json=body).status_code == 403          # doctor can't book
    assert "10:00" not in c.get(f"/api/doctors/1/slots?date={DAY}", headers=H(p)).json()
    assert c.put(f"/api/appointments/{aid}", headers=H(p), json={"status": "CONFIRMED"}).status_code == 400   # patient can't confirm
    assert c.put(f"/api/appointments/{aid}", headers=H(d), json={"status": "CONFIRMED"}).json()["status"] == "CONFIRMED"
    assert len(c.get("/api/appointments", headers=H(d)).json()) == 1

def test_records_and_prescriptions():
    p, d = login("p1@x.com"), login("d1@x.com")
    pid = c.get("/api/appointments", headers=H(d)).json()[0]["patient_id"]
    assert c.post("/api/medical-records", headers=H(d), json={"patient_id": pid, "diagnosis": "Flu", "notes": "Rest"}).status_code == 201
    assert c.post("/api/prescriptions", headers=H(d), json={"patient_id": pid, "medicine_name": "Paracetamol", "dosage": "500mg", "frequency": "TID", "duration": "5d"}).status_code == 201
    assert len(c.get("/api/medical-records", headers=H(p)).json()) == 1
    assert len(c.get("/api/prescriptions", headers=H(p)).json()) == 1
    c.post("/api/auth/register", json={"name": "Pat Two", "email": "p2@x.com", "password": PW})
    assert c.post("/api/medical-records", headers=H(d), json={"patient_id": 999, "diagnosis": "Nope"}).status_code == 403   # unrelated patient
    assert c.get("/api/medical-records", headers=H(login("p2@x.com"))).json() == []                                       # data isolation
