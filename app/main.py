from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth import router as auth_router
from app.modules.employee import emp_router
from app.modules.attendance import attendance_router
from app.core.database import engine
from app.core.config import DATABASE_URL


app = FastAPI(title="Human Resource Management System API", version="1.0.0")



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,   # set True only if using cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}



app.include_router(auth_router)
app.include_router(emp_router)
app.include_router(attendance_router)


@app.on_event("startup")
async def on_startup():
    """Ensure database schema exists before accepting requests.

    The preferred mechanism is to run Alembic migrations; if Alembic is not
    configured or there are no migrations yet, fall back to creating tables
    directly via ``init_models()`` (development only).
    """
    try:
        # attempt to run alembic migrations programmatically
        from alembic import command
        from alembic.config import Config as AlembicConfig
        import os

        alembic_cfg = AlembicConfig(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        command.upgrade(alembic_cfg, "head")
    except Exception as mig_exc:  # pragma: no cover - migrations may not be present
        # typically this will be an OperationalError if the database is
        # unreachable or credentials are wrong. fall back to create_all so
        # developers can still run locally with a different configuration.
        print("Alembic upgrade failed or not configured, falling back to create_all:", mig_exc)
        try:
            from sqlalchemy.exc import OperationalError
            if isinstance(mig_exc, OperationalError):
                print("OperationalError during migration; verify DATABASE_URL credentials.")
        except ImportError:
            pass
        try:
            # from app.core.database import init_models
            # init_models()
            pass
        except Exception as init_exc:
            print(f"Could not initialize database: {init_exc}")
