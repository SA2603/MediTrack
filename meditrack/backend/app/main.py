import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import r

Base.metadata.create_all(bind=engine)
app = FastAPI(title="MEDTRACK API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(r)

@app.get("/health")
def health(): return {"status": "ok"}
