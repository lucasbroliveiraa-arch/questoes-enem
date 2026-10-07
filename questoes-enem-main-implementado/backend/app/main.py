from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import answers, questions, stats

app = FastAPI(
    title="Questões ENEM API",
    description="API de questões do ENEM (2009-2023), com registro de respostas e estatísticas de estudo.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(stats.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
