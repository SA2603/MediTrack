# MEDTRACK – Patient Healthcare Management System

Role-based healthcare platform (Patient / Doctor / Admin). **React + Vite + Tailwind** frontend, **FastAPI + SQLAlchemy + JWT** backend, **SQLite** (local) or **PostgreSQL** (production).

## Features
- JWT auth, bcrypt password hashing, role-based access on every endpoint
- Patient: dashboard, browse doctors, book appointments (free-slot picker, duplicate-slot protection), cancel pending, medical history, prescriptions (print view), profile
- Doctor: dashboard stats, confirm/complete/cancel appointments, add medical records & prescriptions (only for own patients)
- Admin: statistics + charts, manage users/doctors/patients/appointments
- Seed script, backend tests, Swagger docs

## Folder structure
```
meditrack/
├── backend/  app/{main,database,models,schemas,auth,routers,seed}.py  tests/  requirements.txt  .env.example  meditrack.db (pre-seeded demo DB)
├── frontend/ src/{pages,components,services,context,hooks,App.jsx}  package.json  vercel.json  .env.example
└── README.md
```

## Local setup
**Backend** (Python 3.10+)
```bash
cd backend
python -m venv venv && venv\Scripts\activate      # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                            # Mac/Linux: cp
python -m app.seed                                # (re)creates tables + demo data
uvicorn app.main:app --reload                     # http://localhost:8000/docs
```
**Frontend** (Node 18+, second terminal)
```bash
cd frontend
npm install
copy .env.example .env
npm run dev                                       # http://localhost:5173
```
**Tests:** `cd backend && pip install -r requirements-dev.txt && python -m pytest -q`

## Environment variables
Backend: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=60`, `CORS_ORIGINS` (comma-separated)
Frontend: `VITE_API_URL` (backend base URL, no trailing slash)

## Demo credentials (password `Demo@1234`)
| Role | Email |
|---|---|
| Admin | admin@meditrack.com |
| Doctor | doctor@meditrack.com (also doctor2@meditrack.com) |
| Patient | patient@meditrack.com (also patient2–5@meditrack.com) |

## Deployment
1. **GitHub:** `git init && git add . && git commit -m "MEDTRACK" && git branch -M main && git remote add origin <repo-url> && git push -u origin main`
2. **Database:** create a free PostgreSQL on Neon/Supabase/Render; copy its connection string.
3. **Backend on Render:** New → Web Service → repo, Root Directory `backend`, Build `pip install -r requirements.txt`, Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Env vars: `DATABASE_URL`, `SECRET_KEY` (long random), `CORS_ORIGINS` (your Vercel URL, set after step 4). Open Render Shell → `python -m app.seed` once.
4. **Frontend on Vercel:** Import repo, Root Directory `frontend`, framework Vite, env `VITE_API_URL=https://<your-render-app>.onrender.com`. Deploy, then put the Vercel URL into Render's `CORS_ORIGINS` and redeploy.
5. Verify: open the Vercel URL → log in as a demo user. API docs at `<render-url>/docs`.

## Known limitations / future improvements
Tailwind via CDN (swap to build-time Tailwind for production), no password reset/email, no refresh tokens, free Render tier sleeps when idle, only 30-min slots 09:00–16:30, no file uploads. Ideas: email reminders, doctor schedules, chart library, audit logs.
