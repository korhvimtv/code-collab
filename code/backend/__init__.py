from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import create_db_tables
from routers import auth, users, projects, tasks

app = FastAPI(title="Сode-Collab")

origins = ["http://localhost", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    create_db_tables()

@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)