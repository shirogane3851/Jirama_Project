from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, comptes, employes, logs
from routers.demandes import conge_router, permission_router
from routers.pointages import avertissement_router, pointage_router

app = FastAPI(title="Jirama - Gestion du personnel", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # serveur Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employes.router)
app.include_router(comptes.router)
app.include_router(conge_router)
app.include_router(permission_router)
app.include_router(pointage_router)
app.include_router(avertissement_router)
app.include_router(logs.router)


@app.get("/", tags=["Santé"])
def root():
    return {"status": "ok"}