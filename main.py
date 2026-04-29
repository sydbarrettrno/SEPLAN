from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from database import get_session, init_db
from deps import get_current_user
from routers_agent import router as agent_router
from routers_auth import router as auth_router
from routers_protocolos import router as protocolos_router
from schemas import AnalyzeRequest
from settings import get_settings


settings = get_settings()
WEB_DIR = Path(__file__).resolve().parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Agente WhatsApp SEPLAN API", version="0.2.0", lifespan=lifespan)

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/app/")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/me")
def me(user=Depends(get_current_user)):
    return {"email": user.email, "name": user.name, "is_admin": user.is_admin}


@app.post("/analyze")
def analyze(payload: AnalyzeRequest, user=Depends(get_current_user), session: Session = Depends(get_session)):
    text = payload.text.strip()
    score = min(100, max(0, len(text)))
    result = {
        "user": {"email": user.email},
        "summary": f"Analise sintetica do texto recebido (len={len(text)}).",
        "kpis": {"ComplexidadeAprox": score, "NeuroIndexL10": 8},
        "status": "ok",
    }
    return JSONResponse(result)


app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(protocolos_router)

if WEB_DIR.exists():
    app.mount("/app", StaticFiles(directory=WEB_DIR, html=True), name="app")
