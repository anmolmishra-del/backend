from fastapi import FastAPI

from app.modules.auth import router as auth_router


app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}


app.include_router(auth_router)


@app.on_event("startup")
async def on_startup():
    # Database initialization (optional - try but don't block)
    pass