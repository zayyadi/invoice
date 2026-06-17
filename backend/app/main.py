from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import auth, clients, dashboard, exports, invoices, payments, uploads
from app.core.config import settings
from app.core.database import ensure_database_schema
from app.core.media import configure_media_dirs


app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

media_root, _, _ = configure_media_dirs()

app.mount("/media", StaticFiles(directory=media_root), name="media")

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(invoices.router)
app.include_router(payments.router)
app.include_router(dashboard.router)
app.include_router(uploads.router)
app.include_router(exports.router)


@app.on_event("startup")
def startup() -> None:
    ensure_database_schema()


@app.get("/health")
def health_check():
    return {"status": "ok"}
