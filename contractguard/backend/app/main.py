from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db, SessionLocal
from app.kb.seed import seed_kb
from app.api.routes import auth, contracts, risk, chat, review, exports, usage

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    init_db()
    # Seed Knowledge Base if empty
    db = SessionLocal()
    try:
        from app.db.models.kb_document import KBDocument
        count = db.query(KBDocument).count()
        if count == 0:
            seed_kb(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="ContractGuard API",
    description="AI contract reviewer for rental agreements, job offers, and freelance contracts. "
                "Informational tool, not legal advice.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes under /api/v1
api_v1 = FastAPI()
api_v1.include_router(auth.router)
api_v1.include_router(contracts.router)
api_v1.include_router(risk.router)
api_v1.include_router(chat.router)
api_v1.include_router(review.router)
api_v1.include_router(exports.router)
api_v1.include_router(usage.router)

app.mount("/api/v1", api_v1)
# Also include directly for convenience
app.include_router(auth.router, prefix="/api/v1")
app.include_router(contracts.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(review.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")
app.include_router(usage.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "name": "ContractGuard API",
        "version": "1.0.0",
        "status": "online",
        "disclaimer": "ContractGuard is an informational tool, not legal advice.",
        "docs_url": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "app": "ContractGuard"}
